from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import numpy as np
import faiss
import os
import json

app = FastAPI()

# Directory to store FAISS indexes
INDEX_DIR = "/app/faiss_indexes"
os.makedirs(INDEX_DIR, exist_ok=True)

# In-memory storage of indexes and their metadata
indexes = {}
index_metadata = {}

class VectorData(BaseModel):
    vectors: List[List[float]]
    ids: Optional[List[int]] = None
    metadata: Optional[List[Dict[str, Any]]] = None

class SearchQuery(BaseModel):
    index_name: str
    query_vector: List[float]
    k: int = 5

@app.post("/create_index")
async def create_index(index_name: str, dimension: int, index_type: str = "Flat"):
    if index_name in indexes:
        raise HTTPException(status_code=400, detail=f"Index '{index_name}' already exists")
    
    if index_type == "Flat":
        index = faiss.IndexFlatL2(dimension)
    elif index_type == "IVF":
        quantizer = faiss.IndexFlatL2(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, 100)
        index.train(np.random.random((1000, dimension)).astype(np.float32))
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported index type: {index_type}")
    
    indexes[index_name] = index
    index_metadata[index_name] = {
        "dimension": dimension,
        "index_type": index_type,
        "count": 0,
        "metadata": {}
    }
    
    # Save index to disk
    faiss.write_index(index, f"{INDEX_DIR}/{index_name}.index")
    with open(f"{INDEX_DIR}/{index_name}.metadata.json", "w") as f:
        json.dump(index_metadata[index_name], f)
    
    return {"message": f"Created {index_type} index '{index_name}' with dimension {dimension}"}

@app.post("/add_vectors")
async def add_vectors(index_name: str, data: VectorData):
    if index_name not in indexes:
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")
    
    vectors = np.array(data.vectors).astype(np.float32)
    
    # Validate vector dimensions
    if vectors.shape[1] != index_metadata[index_name]["dimension"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Vector dimension mismatch. Expected {index_metadata[index_name]['dimension']}, got {vectors.shape[1]}"
        )
    
    # If IDs are not provided, use auto-increment IDs
    start_id = index_metadata[index_name]["count"]
    if data.ids is None:
        ids = np.arange(start_id, start_id + len(vectors)).astype(np.int64)
    else:
        if len(data.ids) != len(vectors):
            raise HTTPException(status_code=400, detail="Number of IDs must match number of vectors")
        ids = np.array(data.ids).astype(np.int64)
    
    # Store metadata if provided
    if data.metadata:
        if len(data.metadata) != len(vectors):
            raise HTTPException(status_code=400, detail="Number of metadata items must match number of vectors")
        for i, meta in zip(ids, data.metadata):
            index_metadata[index_name]["metadata"][str(i)] = meta
    
    # Add vectors to index
    indexes[index_name].add_with_ids(vectors, ids)
    index_metadata[index_name]["count"] += len(vectors)
    
    # Save updated index and metadata
    faiss.write_index(indexes[index_name], f"{INDEX_DIR}/{index_name}.index")
    with open(f"{INDEX_DIR}/{index_name}.metadata.json", "w") as f:
        json.dump(index_metadata[index_name], f)
    
    return {"message": f"Added {len(vectors)} vectors to index '{index_name}'"}

@app.post("/search")
async def search(query: SearchQuery):
    if query.index_name not in indexes:
        raise HTTPException(status_code=404, detail=f"Index '{query.index_name}' not found")
    
    query_vector = np.array([query.query_vector]).astype(np.float32)
    
    # Validate query vector dimension
    if query_vector.shape[1] != index_metadata[query.index_name]["dimension"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Query vector dimension mismatch. Expected {index_metadata[query.index_name]['dimension']}, got {query_vector.shape[1]}"
        )
    
    # Perform search
    distances, indices = indexes[query.index_name].search(query_vector, query.k)
    
    # Get metadata for results if available
    results = []
    for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
        if idx == -1:  # No more results
            break
        
        result = {
            "id": int(idx),
            "distance": float(dist)
        }
        
        # Add metadata if available
        if str(idx) in index_metadata[query.index_name]["metadata"]:
            result["metadata"] = index_metadata[query.index_name]["metadata"][str(idx)]
        
        results.append(result)
    
    return {"results": results}

@app.get("/list_indexes")
async def list_indexes():
    return {
        "indexes": [
            {
                "name": name,
                "type": meta["index_type"],
                "dimension": meta["dimension"],
                "count": meta["count"]
            } 
            for name, meta in index_metadata.items()
        ]
    }

@app.delete("/delete_index")
async def delete_index(index_name: str):
    if index_name not in indexes:
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")
    
    # Delete from memory
    del indexes[index_name]
    del index_metadata[index_name]
    
    # Delete files
    index_path = f"{INDEX_DIR}/{index_name}.index"
    meta_path = f"{INDEX_DIR}/{index_name}.metadata.json"
    
    if os.path.exists(index_path):
        os.remove(index_path)
    if os.path.exists(meta_path):
        os.remove(meta_path)
    
    return {"message": f"Deleted index '{index_name}'"}

# Load existing indexes on startup
@app.on_event("startup")
async def load_existing_indexes():
    for filename in os.listdir(INDEX_DIR):
        if filename.endswith(".index"):
            index_name = filename.split(".")[0]
            meta_file = f"{INDEX_DIR}/{index_name}.metadata.json"
            
            if os.path.exists(meta_file):
                with open(meta_file, "r") as f:
                    meta = json.load(f)
                    index_metadata[index_name] = meta
                
                index = faiss.read_index(f"{INDEX_DIR}/{index_name}.index")
                indexes[index_name] = index
                print(f"Loaded index '{index_name}' with {meta['count']} vectors")