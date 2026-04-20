import json
import os
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class TurkicOntologyExplorer:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.archive_data = []
        self.load_data()
        self.console = Console(force_terminal=True, color_system="truecolor") if RICH_AVAILABLE else None
        if self.console:
            # Force UTF-8 for Windows legacy terminals if possible
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetConsoleOutputCP(65001)

    def load_data(self):
        if not self.data_dir.exists():
            return
        
        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    self.archive_data.append(json.load(f))
            except Exception as e:
                print(f"Error loading {json_file}: {e}")

    def display_home(self):
        title = "Turkic Ontology Archive - Explorer"
        if RICH_AVAILABLE:
            self.console.print(Panel.fit(f"[bold blue]{title}[/bold blue]\n[italic]Exploring the Eternal Blue Sky and the Sacred Earth[/italic]", border_style="cyan"))
        else:
            print(f"=== {title} ===")
            print("Exploring the Eternal Blue Sky and the Sacred Earth\n")

    def list_categories(self):
        if RICH_AVAILABLE:
            table = Table(title="Available Categories")
            table.add_column("Category", style="cyan")
            table.add_column("Description", style="white")
            
            for item in self.archive_data:
                table.add_row(item["category"], item["description"])
            self.console.print(table)
        else:
            print("Available Categories:")
            for item in self.archive_data:
                print(f"- {item['category']}: {item['description']}")

    def search_concept(self, query):
        results = []
        query = query.lower()
        for category_data in self.archive_data:
            for concept in category_data["concepts"]:
                if query in concept["term"].lower() or query in concept["meaning"].lower():
                    results.append((category_data["category"], concept))
        
        if not results:
            self._safe_print(f"No concepts found for '{query}'", style="red")
            return

        if RICH_AVAILABLE:
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Category", style="magenta")
            table.add_column("Term", style="bold green")
            table.add_column("Orhun", style="yellow")
            table.add_column("Meaning", style="white")
            
            for cat, concept in results:
                table.add_row(cat, concept["term"], concept.get("orhun", ""), concept["meaning"])
            self._safe_print(table)
        else:
            for cat, concept in results:
                print(f"[{cat}] {concept['term']}: {concept['meaning']}")

    def _safe_print(self, content, style=None):
        """Prints content safely, handling encoding errors by stripping non-encodable characters."""
        try:
            if self.console and RICH_AVAILABLE:
                self.console.print(content, style=style)
            else:
                print(content)
        except UnicodeEncodeError:
            if RICH_AVAILABLE:
                # If it's a table or rich object, we might need a simpler fallback
                self.console.print("[yellow]Note: Some characters couldn't be displayed in your terminal.[/yellow]")
                # We can't easily strip a Table object, so we'll just print a fallback message or try to force it
                sys.stdout.reconfigure(errors="replace")
                self.console.print(content, style=style)
            else:
                print(str(content).encode("ascii", "replace").decode("ascii"))

def main():
    explorer = TurkicOntologyExplorer()
    
    if len(sys.argv) < 2:
        explorer.display_home()
        explorer.list_categories()
        print("\nUsage: python src/explorer.py <concept_name>")
        print("Example: python src/explorer.py Tengri")
        sys.exit(0)

    query = " ".join(sys.argv[1:])
    explorer.search_concept(query)

if __name__ == "__main__":
    main()
