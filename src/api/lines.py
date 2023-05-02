from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from typing import List
from fastapi.params import Query
from src import database as db

router = APIRouter()

"""
Returns char name, movie title, conversation ID, and the text of a single line
"""
@router.get("/lines/{line_id}", tags=["lines"])
def get_line(line_id: int):

    line = db.lines.get(line_id)

    if line:
        character = db.characters.get(line.character_id)
        movie = db.movies.get(line.movie_id)
        conversation_id = line.conversation_id
        line_text = line.line_text
        result = {
            "character_name": character.name,
            "movie_title": movie.title,
            "conversation_id": conversation_id,
            "line_text": line_text
        }
        return result

    raise HTTPException(status_code=404, detail="line not found.")


"""
Returns a list of all the lines spoken in a conversation, ordered by the line number
"""
@router.get("/conversations/{conversation_id}/lines", tags=["lines"])
def get_conversation_lines(conversation_id: int):

    conversation = db.conversations.get(conversation_id)

    if conversation:
        # lines = [db.lines.get(line_id) for line_id in conversation.line_ids]
        lines = [db.lines.get(line_id) for line_id in conversation.line_ids]

        lines.sort(key=lambda line: line.line_sort)
        result = [{"character_name": db.characters[line.character_id].name, "line_text": line.line_text} for line in lines]
        return result

    raise HTTPException(status_code=404, detail="conversation not found.")


"""
Returns a list of all the lines spoken by a character, ordered by the line number
"""
@router.get("/characters/{character_id}/lines", tags=["lines"])
def get_character_lines(character_id: int):

    character = db.characters.get(character_id)

    if character:
        lines = [db.lines.get(line_id) for line_id in db.character_lines[character_id]]
        lines.sort(key=lambda line: line.line_sort)
        result = [{"movie_title": db.movies[line.movie_id].title, "line_text": line.line_text} for line in lines]
        return result

    raise HTTPException(status_code=404, detail="character not found.")