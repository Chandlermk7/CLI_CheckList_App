#!/usr/bin/env python3
import json
import os
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from typing import List, Dict, Any

console = Console()

class ChecklistManager:
    def __init__(self, data_file: str = "checklist_data.json"):
        self.data_file = data_file
        self.checklists = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                console.print("[red]Error: Invalid JSON data. Starting fresh.[/red]")
                return {"items": []}
        return {"items": []}
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.checklists, f, indent=2)
        console.print(f"[green]Data saved to {self.data_file}[/green]")
    
    def add_item(self, description: str, priority: str = "medium"):
        item = {
            "id": len(self.checklists["items"]) + 1,
            "description": description,
            "completed": False,
            "priority": priority
        }
        self.checklists["items"].append(item)
        self.save_data()
        console.print(f"[green]Added item: {description}[/green]")
    
    def list_items(self):
        if not self.checklists["items"]:
            console.print("[yellow]No checklist items found.[/yellow]")
            return
        
        table = Table(title="Checklist Items")
        table.add_column("ID", justify="center", style="cyan")
        table.add_column("Status", justify="center", style="green")
        table.add_column("Description", style="white")
        table.add_column("Priority", justify="center")
        
        for item in self.checklists["items"]:
            status = "✓" if item["completed"] else "○"
            priority_color = {
                "high": "red",
                "medium": "yellow", 
                "low": "green"
            }.get(item["priority"], "white")
            
            table.add_row(
                str(item["id"]),
                status,
                item["description"],
                f"[{priority_color}]{item['priority']}[/{priority_color}]"
            )
        
        console.print(table)
    
    def toggle_item(self, item_id: int):
        for item in self.checklists["items"]:
            if item["id"] == item_id:
                item["completed"] = not item["completed"]
                status = "completed" if item["completed"] else "uncompleted"
                console.print(f"[green]Item {item_id} marked as {status}[/green]")
                self.save_data()
                return
        console.print(f"[red]Item with ID {item_id} not found[/red]")

@click.group()
def cli():
    """CLI Checklist App - Manage your tasks efficiently"""
    pass

@cli.command()
@click.argument('description')
@click.option('--priority', '-p', default='medium', 
              type=click.Choice(['low', 'medium', 'high']),
              help='Priority level for the task')
def add(description, priority):
    """Add a new checklist item"""
    manager = ChecklistManager()
    manager.add_item(description, priority)

@cli.command()
def list():
    """List all checklist items"""
    manager = ChecklistManager()
    manager.list_items()

@cli.command()
@click.argument('item_id', type=int)
def toggle(item_id):
    """Toggle completion status of an item"""
    manager = ChecklistManager()
    manager.toggle_item(item_id)

@cli.command()
def interactive():
    """Interactive mode for managing checklist"""
    manager = ChecklistManager()
    
    while True:
        console.print("\n[bold blue]CLI Checklist Manager[/bold blue]")
        console.print("1. Add item")
        console.print("2. List items") 
        console.print("3. Toggle item")
        console.print("4. Exit")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            description = Prompt.ask("Enter task description")
            priority = Prompt.ask("Enter priority", 
                                choices=["low", "medium", "high"], 
                                default="medium")
            manager.add_item(description, priority)
        elif choice == "2":
            manager.list_items()
        elif choice == "3":
            manager.list_items()
            try:
                item_id = int(Prompt.ask("Enter item ID to toggle"))
                manager.toggle_item(item_id)
            except ValueError:
                console.print("[red]Invalid ID entered[/red]")
        elif choice == "4":
            console.print("[green]Goodbye![/green]")
            break

if __name__ == "__main__":
    cli()