import requests
import unittest
import json
from datetime import datetime

class TestDocSyncAPI(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:8000"
        self.test_doc = {
            "id": 1,
            "title": "Test Document",
            "content": "This is a test document",
            "version": 1,
            "tags": ["test", "document"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

    def test_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_create_document(self):
        """Test document creation"""
        response = requests.post(
            f"{self.base_url}/v1/documents/",
            json=self.test_doc
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], self.test_doc["title"])
        self.assertEqual(data["content"], self.test_doc["content"])

    def test_get_document(self):
        """Test getting a single document"""
        # First create a document
        create_response = requests.post(
            f"{self.base_url}/v1/documents/",
            json=self.test_doc
        )
        self.assertEqual(create_response.status_code, 201)
        doc_id = str(self.test_doc["id"])

        # Then retrieve it
        get_response = requests.get(
            f"{self.base_url}/v1/documents/{doc_id}"
        )
        self.assertEqual(get_response.status_code, 200)
        data = get_response.json()
        self.assertEqual(data["title"], self.test_doc["title"])

    def test_list_documents(self):
        """Test listing all documents"""
        # Create a test document first
        requests.post(
            f"{self.base_url}/v1/documents/",
            json=self.test_doc
        )

        # Get list of documents
        response = requests.get(f"{self.base_url}/v1/documents/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertIn("skip", data)
        self.assertIn("limit", data)
        self.assertIsInstance(data["items"], list)
        self.assertGreater(len(data["items"]), 0)
        self.assertGreater(data["total"], 0)

    def test_document_not_found(self):
        """Test getting a non-existent document"""
        response = requests.get(
            f"{self.base_url}/v1/documents/99999"
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_document_data(self):
        """Test creating document with invalid data"""
        invalid_doc = {
            "title": "Invalid Doc",  # Missing required fields
        }
        response = requests.post(
            f"{self.base_url}/v1/documents/",
            json=invalid_doc
        )
        self.assertEqual(response.status_code, 422)  # Validation error

    def test_list_documents_pagination(self):
        """Test paginated document listing"""
        # Create multiple test documents
        docs = [
            {**self.test_doc, "id": i, "title": f"Test Document {i}"} 
            for i in range(1, 15)
        ]
        for doc in docs:
            requests.post(f"{self.base_url}/v1/documents/", json=doc)

        # Test first page
        response = requests.get(f"{self.base_url}/v1/documents/?skip=0&limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["items"]), 5)
        self.assertGreaterEqual(data["total"], 14)
        self.assertEqual(data["skip"], 0)
        self.assertEqual(data["limit"], 5)

        # Test second page
        response = requests.get(f"{self.base_url}/v1/documents/?skip=5&limit=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["items"]), 5)

    def test_document_history(self):
        """Test document history retrieval"""
        # Create a document
        create_response = requests.post(
            f"{self.base_url}/v1/documents/",
            json=self.test_doc
        )
        self.assertEqual(create_response.status_code, 201)
        doc_id = str(self.test_doc["id"])

        # Get document history
        history_response = requests.get(
            f"{self.base_url}/v1/documents/{doc_id}/history"
        )
        self.assertEqual(history_response.status_code, 200)
        history = history_response.json()
        self.assertIsInstance(history, list)
        self.assertGreaterEqual(len(history), 1)

        # Verify history entry fields
        entry = history[0]
        self.assertEqual(entry["document_id"], self.test_doc["id"])
        self.assertEqual(entry["content"], self.test_doc["content"])
        self.assertEqual(entry["version"], self.test_doc["version"])
        self.assertIn("timestamp", entry)

    def test_invalid_pagination_params(self):
        """Test invalid pagination parameters"""
        # Test negative skip
        response = requests.get(f"{self.base_url}/v1/documents/?skip=-1")
        self.assertEqual(response.status_code, 422)

        # Test limit too large
        response = requests.get(f"{self.base_url}/v1/documents/?limit=101")
        self.assertEqual(response.status_code, 422)

        # Test invalid limit
        response = requests.get(f"{self.base_url}/v1/documents/?limit=0")
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
