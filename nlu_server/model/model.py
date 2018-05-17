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

sentence_slot = db.Table('sentence_slot',
    db.Column('sentence_id', db.String(32), db.ForeignKey('sentence.sentence_id'), primary_key=True),
    db.Column('slot_id', db.String(32), db.ForeignKey('slot.slot_id'), primary_key=True)
)

slot_prompt = db.Table('slot_prompt',
    db.Column('slot_id', db.String(32), db.ForeignKey('slot.slot_id'), primary_key=True),
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
    slot = db.relationship('Slot', secondary=sentence_slot, lazy='select',
                backref=db.backref('sentence', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Sentence %r>' % (self.sentence_id)

class Slot(db.Model):

	# __tablename__ = 'slot'

    slot_id = db.Column(db.String(32), nullable=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    slot_type = db.Column(db.Text, nullable=False)
    required = db.Column(db.Boolean, default=False, nullable=False)
    entity_id = db.Column(db.String(32), nullable=False)
    entity_name = db.Column(db.Text, nullable=False)
    prompt = db.relationship('Prompt', secondary=slot_prompt, lazy='select',
            backref=db.backref('slot', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Slot %r>' % (self.slot_id)

class Prompt(db.Model):

	# __tablename__ = 'prompt'

    prompt_id = db.Column(db.String(32), nullable=True, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
    prompt_type = db.Column(db.String(10), nullable=False)
    action_type = db.Column(db.String(10), nullable=False) 

    def __repr__(self):
        return '<Prompt %r>' % self.prompt_id


entity_value = db.Table('entity_value',
    db.Column('entity_id', db.String(32), db.ForeignKey('entity.entity_id'), primary_key=True),
    db.Column('value_id', db.String(32), db.ForeignKey('value.value_id'), primary_key=True)
)

tagtext_value = db.Table('tagtext_value',
    db.Column('tagtext_id', db.String(32), db.ForeignKey('tagtext.tagtext_id'), primary_key=True),
    db.Column('value_id', db.String(32), db.ForeignKey('value.value_id'), primary_key=True)
)


class Entity(db.Model):

	# __tablename__ = 'entity'

    entity_id = db.Column(db.String(32), nullable=True, primary_key=True)
    entity_name = db.Column(db.Text, nullable=False)
    entity_type = db.Column(db.Text, nullable=False)
    entity_extractor = db.Column(db.String(80), nullable=False)
    value = db.relationship('Value', secondary=entity_value, lazy='select',
            backref=db.backref('entity', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Entity %r>' % (self.entity_id)

class Tagtext(db.Model):

	# __tablename__ = 'tagtext'

    tagtext_id = db.Column(db.String(32), nullable=True, primary_key=True)
    tagtext_title = db.Column(db.Text, nullable=False)
    tagtext_content = db.Column(db.Text, nullable=False)
    value = db.relationship('Value', secondary=tagtext_value, lazy='select',
            backref=db.backref('tagtext', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Tagtext %r>' % self.tagtext_id

class Value(db.Model):

	# __tablename__ = 'value'

    value_id = db.Column(db.String(32), nullable=True, primary_key=True)
    value = db.Column(db.Text, nullable=False)
    value_start = db.Column(db.Integer, nullable=False)
    value_end = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Value %r>' % self.value_id


class Model(db.Model):

	# __tablename__ = 'model'

    model_id = db.Column(db.String(32), nullable=True, primary_key=True)
    model_name = db.Column(db.String(80), nullable=False)
    model_path = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Model %r>' % self.model_id