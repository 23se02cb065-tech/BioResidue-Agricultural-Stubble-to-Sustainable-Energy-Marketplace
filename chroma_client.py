import os
import logging
from flask import current_app

try:
    import chromadb
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False

logger = logging.getLogger(__name__)

class ChromaResidueClient:
    def __init__(self, persist_directory=None):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None

    def _get_client_and_collection(self):
        """Lazy initialization of ChromaDB client and collection."""
        if not HAS_CHROMA:
            return None, None
            
        if self.client is not None and self.collection is not None:
            return self.client, self.collection

        # If not initialized, try to load it
        try:
            directory = self.persist_directory or current_app.config['CHROMA_PERSIST_DIRECTORY']
            # Ensure parent directory exists
            os.makedirs(directory, exist_ok=True)
            
            logger.info(f"Initializing ChromaDB persistent client at {directory}")
            self.client = chromadb.PersistentClient(path=directory)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="crop_residues",
                metadata={"hnsw:space": "cosine"} # Using cosine similarity
            )
            return self.client, self.collection
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            # Return None, routes should handle this gracefully
            return None, None

    def index_residue(self, residue):
        """Index or update a residue listing in ChromaDB."""
        client, collection = self._get_client_and_collection()
        if collection is None:
            logger.warning("ChromaDB collection not available. Skipping indexing.")
            return False

        try:
            # Construct a rich text document for embedding generation
            document = (
                f"Crop Type: {residue.crop_type}. "
                f"Description: {residue.description or 'No description provided'}. "
                f"Location: {residue.location_name}."
            )
            
            # Metadata allows us to filter or display basic info directly
            metadata = {
                "id": residue.id,
                "crop_type": residue.crop_type,
                "quantity": float(residue.quantity),
                "price_per_unit": float(residue.price_per_unit),
                "latitude": float(residue.latitude),
                "longitude": float(residue.longitude),
                "location_name": residue.location_name,
                "farmer_id": residue.farmer_id
            }

            # Upsert into ChromaDB
            collection.upsert(
                documents=[document],
                metadatas=[metadata],
                ids=[str(residue.id)]
            )
            logger.info(f"Successfully indexed residue ID {residue.id} in ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error indexing residue ID {residue.id} in ChromaDB: {str(e)}")
            return False

    def remove_residue(self, residue_id):
        """Remove a residue listing from ChromaDB."""
        client, collection = self._get_client_and_collection()
        if collection is None:
            return False
        
        try:
            collection.delete(ids=[str(residue_id)])
            logger.info(f"Removed residue ID {residue_id} from ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error removing residue ID {residue_id} from ChromaDB: {str(e)}")
            return False

    def search_residues(self, query_text, limit=10):
        """Perform semantic search on crop residues using the default embedding function."""
        client, collection = self._get_client_and_collection()
        if collection is None:
            logger.warning("ChromaDB collection not available. Returning None to trigger SQL search fallback.")
            return None

        try:
            results = collection.query(
                query_texts=[query_text],
                n_results=limit
            )
            
            # Format the output into structured dictionaries
            formatted_results = []
            if results and 'ids' in results and len(results['ids']) > 0:
                ids = results['ids'][0]
                metadatas = results['metadatas'][0] if 'metadatas' in results and results['metadatas'] else []
                documents = results['documents'][0] if 'documents' in results and results['documents'] else []
                distances = results['distances'][0] if 'distances' in results and results['distances'] else []
                
                for i in range(len(ids)):
                    formatted_results.append({
                        "id": int(ids[i]),
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                        "document": documents[i] if i < len(documents) else "",
                        "distance": float(distances[i]) if i < len(distances) else 0.0
                    })
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            return []

# Create a global instance that will lazy-initialize when first accessed
chroma_client = ChromaResidueClient()
