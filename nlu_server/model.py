from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


from flask_sqlalchemy import SQLAlchemy

from nlu_server.shared import db

intent_sentence = db.Table('intent_sentence',
    db.Column('intent_id', db.String(32), db.ForeignKey('intent.intent_id'), primary_key=True),
    db.Column('sentence_id', db.String(32), db.ForeignKey('sentence.sentence_id'), primary_key=True)
)

intent_prompt = db.Table('intent_prompt',
    db.Column('intent_id', db.String(32), db.ForeignKey('intent.intent_id'), primary_key=True),
    db.Column('prompt_id', db.String(32), db.ForeignKey('prompt.prompt_id'), primary_key=True)
)

sentence_entity = db.Table('sentence_entity',
    db.Column('sentence_id', db.String(32), db.ForeignKey('sentence.sentence_id'), primary_key=True),
    db.Column('entity_id', db.String(32), db.ForeignKey('entity.entity_id'), primary_key=True)
)

entity_prompt = db.Table('entity_prompt',
    db.Column('entity_id', db.String(32), db.ForeignKey('entity.entity_id'), primary_key=True),
    db.Column('prompt_id', db.String(32), db.ForeignKey('prompt.prompt_id'), primary_key=True)
)

class Intent(db.Model):

	# __tablename__ = 'intent'
    
    intent_id = db.Column(db.String(32), nullable=True, primary_key=True)
    intent_name = db.Column(db.Text, nullable=False)
    bot_id = db.Column(db.String(32), nullable=False)
    node_id = db.Column(db.String(32), nullable=False)
    flow_id = db.Column(db.String(32), nullable=False)
    create_date = db.Column(db.DATETIME, nullable=False)
    update_date = db.Column(db.DATETIME, nullable=False)  
    sentence = db.relationship('Sentence', secondary=intent_sentence, lazy='select',
        backref=db.backref('intent', lazy=True), cascade="all,delete")
    prompt = db.relationship('Prompt', secondary=intent_prompt, lazy='select',
        backref=db.backref('intent', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Intent %r>' % (self.intent_id)

class Sentence(db.Model):

	# __tablename__ = 'sentence'

    sentence_id = db.Column(db.String(32), nullable=True, primary_key=True)
    sentence = db.Column(db.Text, nullable=False)
    entity = db.relationship('Entity', secondary=sentence_entity, lazy='select',
                backref=db.backref('sentence', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Sentence %r>' % (self.sentence_id)

class Entity(db.Model):

	# __tablename__ = 'entity'

    entity_id = db.Column(db.String(32), nullable=True, primary_key=True)
    value = db.Column(db.Text, nullable=False)
    entity = db.Column(db.Text, nullable=False)
    entity_type = db.Column(db.String(10), nullable=False)
    start_sentence = db.Column(db.Integer, nullable=False)
    end_sentence = db.Column(db.Integer, nullable=False)
    prompt = db.relationship('Prompt', secondary=entity_prompt, lazy='select',
            backref=db.backref('entity', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Entity %r>' % (self.entity_id)

class Prompt(db.Model):

	# __tablename__ = 'prompt'

    prompt_id = db.Column(db.String(32), nullable=True, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
    prompt_type = db.Column(db.String(10), nullable=False)
    action_type = db.Column(db.String(10), nullable=False) 

    def __repr__(self):
        return '<Prompt %r>' % self.prompt_id