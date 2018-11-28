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

intent_slot = db.Table('intent_slot',
    db.Column('intent_id', db.String(32), db.ForeignKey('intent.intent_id'), primary_key=True),
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
    admin_id = db.Column(db.String(32), nullable=False)
    model_id = db.Column(db.String(32), nullable=False)
    create_date = db.Column(db.DATETIME, nullable=False)
    update_date = db.Column(db.DATETIME, nullable=False)  
    sentence = db.relationship('Sentence', secondary=intent_sentence, lazy='select',
        backref=db.backref('intent', lazy=True), cascade="all,delete")
    slot = db.relationship('Slot', secondary=intent_slot, lazy='select',
        backref=db.backref('intent', lazy=True), cascade="all,delete")
    prompt = db.relationship('Prompt', secondary=intent_prompt, lazy='select',
        backref=db.backref('intent', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Intent %r>' % (self.intent_id)

class Sentence(db.Model):

	# __tablename__ = 'sentence'

    sentence_id = db.Column(db.String(32), nullable=True, primary_key=True)
    sentence = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Sentence %r>' % (self.sentence_id)

class Slot(db.Model):

	# __tablename__ = 'slot'

    slot_id = db.Column(db.String(32), nullable=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    required = db.Column(db.Boolean, default=False, nullable=False)
    entity_id = db.Column(db.String(32), db.ForeignKey('entity.entity_id'))
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

article_entity_value = db.Table('article_entity_value',
    db.Column('article_id', db.String(32), db.ForeignKey('article.article_id'), primary_key=True),
    db.Column('entity_value_id', db.String(32), db.ForeignKey('entity_value.entity_value_id'), primary_key=True)
)

class Entity(db.Model):

	# __tablename__ = 'entity'

    entity_id = db.Column(db.String(32), nullable=True, primary_key=True)
    entity_name = db.Column(db.Text, nullable=False)
    entity_type = db.Column(db.Text, nullable=False)
    entity_extractor = db.Column(db.String(80), nullable=False)
    duckling_name = db.Column(db.String(80), nullable=False)
    admin_id = db.Column(db.String(80), nullable=False)
    model_id = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return '<Entity %r>' % (self.entity_id)

class Article(db.Model):

	# __tablename__ = 'article'

    article_id = db.Column(db.String(32), nullable=True, primary_key=True)
    article_title = db.Column(db.Text, nullable=False)
    article_content = db.Column(db.Text, nullable=False)
    admin_id = db.Column(db.String(80), nullable=False)
    model_id = db.Column(db.String(32), nullable=False)
    create_date = db.Column(db.DATETIME, nullable=False)
    update_date = db.Column(db.DATETIME, nullable=False) 
    entity_value = db.relationship('EntityValue', secondary=article_entity_value, lazy='select',
            backref=db.backref('article', lazy=True), cascade="all,delete")

    def __repr__(self):
        return '<Article %r>' % self.tagtext_id

class EntityValue(db.Model):

	# __tablename__ = 'entity_value'

    entity_value_id = db.Column(db.String(32), nullable=True, primary_key=True)
    entity_value = db.Column(db.Text, nullable=False)
    synonyms = db.Column(db.Text, nullable=False)
    value_start = db.Column(db.Integer, nullable=False)
    value_end = db.Column(db.Integer, nullable=False)
    value_from = db.Column(db.String(32), nullable=False)
    entity_id = db.Column(db.String(32), nullable=False)

    def __repr__(self):
        return '<EntityValue %r>' % self.entity_value_id

model_node= db.Table('model_node',
    db.Column('model_id', db.String(32), db.ForeignKey('model.model_id'), primary_key=True),
    db.Column('node_id', db.String(32), db.ForeignKey('node.node_id'), primary_key=True)
)

class Model(db.Model):

	# __tablename__ = 'model'

    model_id = db.Column(db.String(32), nullable=True, primary_key=True)
    model_name = db.Column(db.String(80), nullable=False)
    model_path = db.Column(db.String(255), nullable=False)
    mitie_embeding_path = db.Column(db.String(255), nullable=False)
    w2v_embeding_path = db.Column(db.String(255), nullable=False)
    w2v_embeding_type = db.Column(db.String(20), nullable=False)
    admin_id = db.Column(db.String(32), nullable=False)
    node = db.relationship('Node', secondary=model_node, lazy='select',
            backref=db.backref('model', lazy=True), cascade="all,delete",
            order_by='Node.order')

    def __repr__(self):
        return '<Model %r>' % self.model_id

class Admin(db.Model):

	# __tablename__ = 'admin'

    admin_id = db.Column(db.String(32), nullable=True, primary_key=True)
    admin_name = db.Column(db.String(80), nullable=False)
    available = db.Column(db.Boolean, nullable=False)
    create_date = db.Column(db.DATETIME, nullable=False)
    update_date = db.Column(db.DATETIME, nullable=False)

    def __repr__(self):
        return '<Admin %r>' % self.admin_id


class Node(db.Model):

	# __tablename__ = 'node'

    node_id = db.Column(db.String(32), nullable=True, primary_key=True)
    class_name = db.Column(db.String(80), nullable=False)
    module_name = db.Column(db.String(80), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Node %r>' % self.node_id