from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter

from typing import List
from fastapi.params import Query
from src import database as db
import sqlalchemy as sq
router = APIRouter()

"""
Returns char name, movie title, conversation ID, and the text of a single line
"""
@router.get("/lines/{line_id}", tags=["lines"])
def get_line(line_id: int):


    stmt = (sq.select(db.characters.c.name, db.movies.c.title, 
                      db.conversations.c.conversation_id, db.lines.c.line_text)
                      .select_from(db.lines.join(db.characters, db.lines.c.character_id == db.characters.c.character_id)
                                   .join(db.movies, db.characters.c.movie_id == db.movies.c.movie_id))
                      .where(db.lines.c.line_id == line_id))
    
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        line = []
        for row in result:
            line.append(
                {
                    "character_name": row.name,
                    "movie_title": row.title,
                    "conversation_id": row.conversation_id,
                    "line_text": row.line_text
                }
            )

    return line

    # line = db.lines.get(line_id)

    # if line:
    #     character = db.characters.get(line.character_id)
    #     movie = db.movies.get(line.movie_id)
    #     conversation_id = line.conversation_id
    #     line_text = line.line_text
    #     result = {
    #         "character_name": character.name,
    #         "movie_title": movie.title,
    #         "conversation_id": conversation_id,
    #         "line_text": line_text
    #     }
    #     return result

    # raise HTTPException(status_code=404, detail="line not found.")


"""
Returns a list of all the lines spoken in a conversation, ordered by the line number
line num, char name, line
"""
@router.get("/conversations/{conversation_id}/lines", tags=["lines"])
def get_conversation_lines(conversation_id: int):


    stmt = (sq.select(db.lines.c.line_id, db.characters.c.name, db.lines.c.line_text)
            .select_from(db.lines.join(db.characters, db.lines.c.character_id == db.characters.c.character_id))
            .where(db.lines.c.conversation_id == conversation_id)
            .order_by(sq.asc('line_id')))
    
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        cvlines = []
        for row in result:
            cvlines.append(
                {
                    "line_id": row.line_id,
                    "name": row.name,
                    "line_text": row.line_text
                }
            )

    return cvlines


    # conversation = db.conversations.get(conversation_id)

    # if conversation:
    #     # lines = [db.lines.get(line_id) for line_id in conversation.line_ids]
    #     lines = [db.lines.get(line_id) for line_id in conversation.line_ids]

    #     lines.sort(key=lambda line: line.line_sort)
    #     result = [{"character_name": db.characters[line.character_id].name, "line_text": line.line_text} for line in lines]
    #     return result

    # raise HTTPException(status_code=404, detail="conversation not found.")


"""
Returns a list of all the lines spoken by a character, ordered by the line number
line num, recipient(who the char was speaking to), line_text
"""
@router.get("/characters/{character_id}/lines", tags=["lines"])
def get_character_lines(character_id: int):

    stmt = (sq.select(db.lines.c.line_id, db.characters.c.name, db.lines.c.line_text)
            .select_from(db.lines.join(db.conversations, db.lines.c.conversation_id == db.conversations.c.conversation_id)
                         .join(db.characters, db.conversations.c.character2_id ==  db.characters.c.character_id))
                         .where(db.characters.c.character_id == character_id)
                         .order_by(sq.asc('line_id')))
    
    
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        chlines = []
        for row in result:
            chlines.append(
                {
                    "line_id": row.line_id,
                    "recipient": row.name,
                    "line_text": row.line_text
                }
            )

    return chlines
    # character = db.characters.get(character_id)

    # if character:
    #     lines = [db.lines.get(line_id) for line_id in db.character_lines[character_id]]
    #     lines.sort(key=lambda line: line.line_sort)
    #     result = [{"movie_title": db.movies[line.movie_id].title, "line_text": line.line_text} for line in lines]
    #     return result

    # raise HTTPException(status_code=404, detail="character not found.")