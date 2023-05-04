from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlalchemy as sq

# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """

    # # TODO: Remove the following two lines. This is just a placeholder to show
    # # how you could implement persistent storage.

    # print(conversation)
    # db.logs.append({"post_call_time": datetime.now(), "movie_id_added_to": movie_id})
    # db.upload_new_log()


    c1_id = conversation.character_1_id
    c2_id = conversation.character_2_id

    stmt = (sq.select(db.characters.c.character_id, db.movies.c.movie_id)
               .select_from(db.characters.join(db.movies, db.characters.c.movie_id == db.movies.c.movie_id))
               .where(db.characters.c.character_id == c1_id))
   
    with db.engine.connect() as conn: 
        result = conn.execute(stmt)

    c1 = result.first()

    if c1 is None:
        raise HTTPException(status_code=404, detail=f"Character not found.")
    
    if c1.movie_id != movie_id:
        raise HTTPException(status_code=404, detail=f"Character not found in movie.")

    stmt = (sq.select(db.characters.c.character_id, db.movies.c.movie_id)
               .select_from(db.characters.join(db.movies, db.characters.c.movie_id == db.movies.c.movie_id))
               .where(db.characters.c.character_id == c2_id))
    
    with db.engine.connect() as conn: 
        result = conn.execute(stmt)

    c2 = result.first()

    if c2 is None:
        raise HTTPException(status_code=404, detail=f"Character not found.")
    
    if c2.movie_id != movie_id:
        raise HTTPException(status_code=404, detail=f"Character not found in movie.")


    if c1.character_id == c2.character_id:
        raise HTTPException(status_code=404, detail="Characters must be different")
    
    for line in conversation.lines:
        if line.character_id != c1.character_id and line.character_id != c2.character_id:
            raise HTTPException(status_code=404, detail=f"Character(s) not found in movie.")


    last_conv = (sq.select(db.conversations.c.conversation_id).order_by(sq.desc(db.conversations.c.conversation_id)).limit(1))
    last_line = (sq.select(db.lines.c.line_id).order_by(sq.desc(db.lines.c.line_id)).limit(1))

    with db.engine.begin() as conn:
        conv_id = conn.execute(last_conv)
        
        for id in conv_id:
            new_conv_id = id.conversation_id + 1

        new_conv = (db.conversations.insert().values(
            conversation_id = conv_id,
            character1_id = c1_id,
            character2_id = c2_id,
            movie_id = movie_id
        ))

        conn.execute(new_conv, [{"conv_id": new_conv_id,
                                 "c1_id": conversation.character_1_id,
                                 "c2_id": conversation.character_2_id,
                                 "movie_id": movie_id
                                 }]
        )

        line_id = conn.execute(last_line)

        for id in line_id:
            new_line_id = id.line_id + 1

        line_sort = 1

        for line in conversation.lines:
            new_line =  (db.lines.insert().values(
                line_id = line_id,
                character_id = line.character_id,
                movie_id = movie_id,
                conversation_id = new_conv_id,
                line_sort = line_sort,
                line_text = line.line_text
            ))
            conn.execute(new_line,[{"line_id": new_line_id, 
                                    "character_id": line.character_id,
                                    "movie_id": movie_id,
                                    "conversation_id": new_conv_id,
                                    "line_sort": line_sort,
                                    "line_text": line.line_text
                                    }]
            )

            new_line_id += 1
            line_sort += 1

    
    # # movie exists check
    # movie = db.get_movie(movie_id)
    # if movie is None:
    #     raise HTTPException(status_code=404, detail="Movie not found.")

    # # characters are in the movie check
    # for character_id in [conversation.character_1_id, conversation.character_2_id]:
    #     if not any(character_id == character.id for character in movie.characters):
    #         raise HTTPException(status_code=404, detail=f"Character(s) not found in movie.")

    # # characters are different check
    # if conversation.character_1_id == conversation.character_2_id:
    #     raise HTTPException(status_code=404, detail="Characters must be different")
    
    # # lines match the character check
    # for line in conversation.lines:
    #     if line.character_id not in [conversation.character_1_id, conversation.character_2_id]:
    #         raise HTTPException(status_code=404, detail=f"Line {line.line_text} does not match characters in conversation.")
        

    # # add conversation
    # new_conversation_id = len(db.conversations)
    # new_conversation = {
    #     "id": new_conversation_id,
    #     "movie_id": movie_id,
    #     "character_1_id": conversation.character_1_id,
    #     "character_2_id": conversation.character_2_id,
    # }
    # db.conversations.append(new_conversation)
    # db.upload_new_conversation()

    # # add/sort lines
    # line_sort = 1
    # for l in conversation.lines:

    #     next_line_id = int(db.char_lines[len(db.char_lines)-1]["line_id"]) + 1

    #     db.char_lines.append({"line_id": next_line_id,
    #                     "character_id": l.character_id,
    #                     "movie_id": movie_id,
    #                     "conversation_id": new_conversation_id,
    #                     "line_sort": line_sort,
    #                     "line_text": l.line_text
    #                     })
    #     line_sort += 1
    
    # db.upload_new_lines()
    
    # # Return the ID of the resulting conversation
    # return {"id": new_conversation_id}


# Edge cases the code does not work well in:
#
# - The function uses a list to store the conversations the code which may not 
# work well when there are multiple simultaneous calls to the function becuase
# it can lead to race conditions where two or more requests try to modify the 
# same data structure at the same time, which can result in unpredictable behavior
# and data corruption.
#
# - There is no check for duplicate conversations, so two identical conversations
# could be created with different IDs.
#
# - If the request body is too large the it might consume too much memory or crash.