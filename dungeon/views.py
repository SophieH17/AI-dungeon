from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
import json
from dotenv import load_dotenv
from .game import AIDungeonGame
import csv
from django.http import FileResponse
import io

load_dotenv()

game_instance = None

def index(request):
    global game_instance    
    if game_instance is None:
        api_key = 'your_openai_api_key_here'  # Replace with your OpenAI API key
        if not api_key:
            return JsonResponse({
                'error': 'OpenAI API key not found'
            }, status=500)
        game_instance = AIDungeonGame(api_key)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                command = data.get('command', '')
                world = data.get('world', 'fantasy')
                custom_description = data.get('customWorldDescription')
                play_style = data.get('playStyle', 'adventure')

                # Handle regular commands
                response = game_instance.process_command(
                    command=command, 
                    world=world,
                    play_style=play_style,
                    custom_description=custom_description
                )
                return JsonResponse({
                    'message': response,
                    'history': game_instance.game_history
                })
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON data'
                }, status=400)
            except Exception as e:
                return JsonResponse({
                    'error': f'An error occurred: {str(e)}'
                }, status=500)
    
    template = loader.get_template('dungeon/index.html')
    return HttpResponse(template.render({}, request))

def download_txt(request):
    if game_instance is None or not game_instance.game_history:
        return HttpResponse("No game history available", status=404)
    
    current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_name = "gpt-4o-mini"
    
    # Convert game history to text format
    content = ""
    for entry in game_instance.game_history:
        if isinstance(entry, dict):
            content += f"{entry['role']}: {entry['content']}\n\n"
        else:
            content += f"{entry}\n\n"
    
    # Return the content directly as text
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{model_name}_{current_date}.txt"'
    return response

def download_csv(request):
    if game_instance is None or not game_instance.game_history:
        return HttpResponse("No game history available", status=404)
    
    current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_name = "gpt-4o-mini"
    
    # Create CSV content directly
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Role', 'Content'])  # Header
    
    for entry in game_instance.game_history:
        if isinstance(entry, dict):
            writer.writerow([entry['role'], entry['content']])
        else:
            writer.writerow(['system', str(entry)])
    
    # Return the CSV content
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{model_name}_{current_date}.csv"'
    return response

def get_world_prompt(world):
    prompts = {
        'fantasy': "You are a narrator in a classic fantasy world with magic, dragons, and epic quests.",
        'harry-potter': "You are a narrator in the Harry Potter universe. The adventure takes place at Hogwarts School of Witchcraft and Wizardry.",
        'star-wars': "You are a narrator in the Star Wars universe. The adventure takes place in a galaxy far, far away.",
        'dnd': "You are a Dungeon Master running a Dungeons & Dragons campaign in the Forgotten Realms setting."
    }
    return prompts.get(world, prompts['fantasy'])

# Update your view to handle the world parameter
def handle_command(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        command = data.get('command')
        world = data.get('world', 'fantasy')
        
        if command == 'start':
            # Initialize new game with selected world
            world_prompt = get_world_prompt(world)
            # Update your game initialization logic to use world_prompt
            ...


    

