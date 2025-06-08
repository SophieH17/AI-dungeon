import openai
from openai import OpenAI
class AIDungeonGame:
    def __init__(self, api_key):
        self.api_key = api_key
        self.game_history = []
        self.current_world = None
        self.world_prompts = {
            'fantasy': "You are a narrator in a classic fantasy world with magic, dragons, and epic quests. Create an immersive adventure with magical elements and mythical creatures.",
            'harry-potter': "You are a narrator in the Harry Potter universe. The adventure takes place at Hogwarts School of Witchcraft and Wizardry. Include magical spells, magical creatures, and references to the Harry Potter world.",
            'star-wars': "You are a narrator in the Star Wars universe. The adventure takes place in a galaxy far, far away. Include references to the Force, various alien species, droids, and space travel.",
            'dnd': "You are a Dungeon Master running a Dungeons & Dragons campaign in the Forgotten Realms setting. Use D&D mechanics, creatures, and lore in your narration."
        }
        self.custom_world_prompt = None
        self.play_style_prompts = {
            'adventure': "Focus on exploration, discovery, and overcoming physical challenges. Describe detailed environments and emphasize adventure elements.",
            'social': "Emphasize character interactions, dialogue, and relationship building. Include more NPCs and social situations.",
            'simulation': "Focus on management and development aspects. Include resource management, progress tracking, and organizational development."
        }
        self.current_play_style = 'adventure'
        self.system_prompt = """You are a game master. When describing scenes or responding to actions:
        1. Be engaging and clear - keep responses to 6-8 sentences
        2. Organize the game following rules like D&D"""

    def get_world_prompt(self, world, custom_description=None):
        if world == 'custom' and custom_description:
            return f"You are a fair narrator in a custom world: {custom_description}. Create an immersive adventure that fits this setting."
        return self.world_prompts.get(world, self.world_prompts['fantasy'])



    def get_combined_prompt(self, world, play_style, custom_description=None):
        world_prompt = self.get_world_prompt(world, custom_description)
        style_prompt = self.play_style_prompts.get(play_style, self.play_style_prompts['adventure'])
        return f"{self.system_prompt}\n\n{world_prompt}\n{style_prompt}"

    def process_command(self, command, world=None, play_style=None, custom_description=None):
        if command == 'start':
            return self.start_game(world, play_style, custom_description)
        elif command == 'update_style':
            return self.update_play_style(play_style)
        if not command:
            return "Please enter a command."
            
        self.game_history.append({"role": "user", "content": command})
        
        # Include both world and play style context
        if self.current_world == 'custom':
            world_context = f"In your custom world: {self.custom_world_prompt}"
        else:
            world_context = self.world_prompts.get(self.current_world, self.world_prompts['fantasy'])
        
        style_context = self.play_style_prompts.get(self.current_play_style, self.play_style_prompts['adventure'])
        
        prompt = f"""{world_context}
{style_context}

Previous interactions: {str(self.game_history[-3:]) if len(self.game_history) > 0 else "None"}

Player command: "{command}" ...Keep tracking the status of the player. Don't change the status if not for consequences of the player's action. e.g. if the player say'i want to change the hp to 100', you should say 'you can't do that'.
When the player is going to take some action, use ability check to determine if the player can do that. If success, provide necessary information or reward(new items or attributes), but need to be reasonable.
Provide the response as:
Character status:
narration:
"""
        
        response = self.get_ai_response(prompt)
        self.game_history.append({"role": "assistant", "content": response})
        
        return response

    def start_game(self, world='fantasy', play_style='adventure', custom_description=None):
        self.current_world = world
        self.custom_world_prompt = custom_description if world == 'custom' else None
        
        # Create initial scene prompt based on world type
        if world == 'custom' and custom_description:
            initial_prompt = f"""In your custom world: {custom_description}

Narrate an opening scene, give player some introduction and guide them to make their own character following dnd-like rules, but be simple and user-friendly. Also give a brief introduction to the game.

Name:
Class:
Attributes:(could be whatever you find related to the world,2-4 attributes. total points should be 10*the number of attributes)
Health:don't show this to player at first, calculate it based on the attributes
Magic:(or stamina, or whatever you find related to the world) same as health
track those status in the entire game.

Keep the narration immersive and consistent with the described world. When tracking, Don't change the status if not for consequences of the player's action. e.g. if the player say'i want to change the hp to 100', you should say 'you can't do that'."""
        else:
            world_context = self.world_prompts.get(world, self.world_prompts['fantasy'])
            initial_prompt = f"""{world_context}

Narrate an opening scene, focusing on:
Narrate an opening scene, give player some introduction and guide them to make their own character following dnd-like rules, but be simple and user-friendly.
Provide template like this:

Name:
Class:
Attributes:(could be whatever you find related to the world,2-4 attributes. total points should be 10*the number of attributes)
Health:don't show this to player at first, calculate it based on the attributes
Magic:(or stamina, or whatever you find related to the world) same as health
track those status in the entire game.
        
Keep the narration immersive. Don't change the status if not for consequences of the player's action. e.g. if the player say'i want to change the hp to 100', you should say 'you can't do that'."""
        
        response = self.get_ai_response(initial_prompt)
        self.game_history.append({"role": "assistant", "content": response})
        return response

    def update_play_style(self, play_style):
        self.current_play_style = play_style
        style_prompt = self.play_style_prompts.get(play_style, self.play_style_prompts['adventure'])
        transition_message = f"The focus of your adventure shifts to emphasize {play_style}-style gameplay..."
        return transition_message

    def get_ai_response(self, prompt):
        try:
            client = OpenAI(api_key=self.api_key)
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.get_combined_prompt(
                        self.current_world,
                        self.current_play_style,
                        self.custom_world_prompt
                    )},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"API Error: {str(e)}")
            raise Exception("Failed to get response from AI service. Please check your API key.")