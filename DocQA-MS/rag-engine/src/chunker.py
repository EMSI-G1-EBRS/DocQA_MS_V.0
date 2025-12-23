import re
import warnings
from typing import List, Dict, Any
from transformers import AutoTokenizer

warnings.filterwarnings("ignore", message=".*sequence length.*")

class MedicalChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            model_max_length=512
        )
        
        self.section_patterns = {
            "anamnese": [
                r"(?:anamnèse|anamnese|histoire|histoire de la maladie)",
                r"(?:motif|raison|consultation)",
                r"(?:antécédents|antecedents)"
            ],
            "diagnostic": [
                r"(?:diagnostic|diagnostique|conclusion)",
                r"(?:impression|impression clinique)",
                r"(?:hypothèse|hypothese diagnostique)"
            ],
            "traitement": [
                r"(?:traitement|therapeutique|thérapeutique)",
                r"(?:prescription|médicaments|medicaments)",
                r"(?:plan de traitement)"
            ],
            "examen": [
                r"(?:examen|examen clinique|examen physique)",
                r"(?:observations|observation)",
                r"(?:signes cliniques)"
            ],
            "evolution": [
                r"(?:évolution|evolution|suivi)",
                r"(?:prognostic|pronostic)",
                r"(?:suivi|follow-up)"
            ]
        }
    
    def detect_sections(self, text: str) -> List[Dict[str, Any]]:
        sections = []
        lines = text.split('\n')
        current_section = None
        current_start = 0
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            detected_type = None
            
            for section_type, patterns in self.section_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line_lower, re.IGNORECASE):
                        detected_type = section_type
                        break
                if detected_type:
                    break
            
            if detected_type and detected_type != current_section:
                if current_section:
                    sections.append({
                        "type": current_section,
                        "start": current_start,
                        "end": i,
                        "text": "\n".join(lines[current_start:i])
                    })
                current_section = detected_type
                current_start = i
        
        if current_section:
            sections.append({
                "type": current_section,
                "start": current_start,
                "end": len(lines),
                "text": "\n".join(lines[current_start:])
            })
        
        if not sections:
            sections.append({
                "type": "general",
                "start": 0,
                "end": len(lines),
                "text": text
            })
        
        return sections
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        print(f"Detecting sections in text of length {len(text)}...", flush=True)
        sections = self.detect_sections(text)
        print(f"Found {len(sections)} sections. Starting chunking...", flush=True)
        chunks = []
        
        for section in sections:
            section_text = section["text"]
            section_type = section["type"]
            
            section_chunks = self._chunk_section(
                section_text,
                section_type,
                metadata or {}
            )
            chunks.extend(section_chunks)
        
        return chunks
    
    def _chunk_section(self, text: str, section_type: str, base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        print(f"Tokenizing section '{section_type}' ({len(text)} chars)...", flush=True)
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        print(f"Generated {len(tokens)} tokens. Splitting into chunks...", flush=True)
        
        if len(tokens) <= self.chunk_size:
            return [{
                "text": text,
                "position": 0,
                "metadata": {
                    **base_metadata,
                    "section_type": section_type,
                    "chunk_index": 0
                }
            }]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            
            chunks.append({
                "text": chunk_text,
                "position": chunk_index,
                "metadata": {
                    **base_metadata,
                    "section_type": section_type,
                    "chunk_index": chunk_index,
                    "token_start": start,
                    "token_end": end
                }
            })
            
            if end == len(tokens):
                break
                
            start = end - self.chunk_overlap
            chunk_index += 1
            
            if chunk_index % 100 == 0:
                print(f"Processed {chunk_index} chunks...", flush=True)
        
        print(f"Finished section. Total chunks: {len(chunks)}", flush=True)
        return chunks

chunker = MedicalChunker()

