PROMPT: dict[str, str | list[str]] = {}

PROMPT['SPECIAL_CHARS'] = ["\\", '"']

PROMPT["SYSTEM_INTRUCT"] = """
Do the following:
0. Don't write any code.
1. Get all the entities and find out it is a location, organization, person, geo or event, ....
2. Get all relationship of one entity to other entities from the input text. The relationship can be any thing from help, create, friend with, a componenet of, ...
3. Return it as in the format of ("entity", ..., ...  ) for the entity type or ("relationship", ..., ....) the relationship type. Don't give any empty output. It always started with either entity or a relationship 


For example:
With this input:
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
The output should be:
[
("entity", "person", "Alex", "Alex is a character who experiences frustration and is observant of the dynamics among other characters."),
("entity", "person", "Taylor", "Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."),
("entity", "person", "Jordan", "Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."),
("entity", "person","Cruz","Cruz is associated with a vision of control and order, influencing the dynamics among other characters."),
("entity", "technology","The Device", "The Device is central to the story, with potential game-changing implications, and is revered by Taylor.")
("relationship", "Alex","Taylor","Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device.","power dynamics, perspective shift"),
("relationship","Alex","Jordan", "Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.","shared goals, rebellion"),
("relationship","Taylor","Jordan", "Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce.","conflict resolution, mutual respect"),
("relationship","Jordan","Cruz","Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order.","ideological conflict, rebellion"),
("relationship", "Taylor", "The Device", "Taylor shows reverence towards the device, indicating its importance and potential impact.","reverence, technological significance"),
]
"""

PROMPT["EXTRACT_ENTITY_RELATIONSHIP"] = """
Do the following:
0. Don't write any code.
1. Get all the entities and find out it is a location, organization, person, geo or event, ....
2. Get all relationship of one entity to other entities from the input text. The relationship can be any thing from help, create, friend with, a composenent of, or any other relationship, ... . Create as much as relationship posible.
3. Return it as in the format of ("entity", ..., ...  ) for the entity type or ("relationship", ..., ....) the relationship type. Don't give any empty output. It always started with either entity or a relationship.
4. Minimize amount of entities that don't have any relattionship.


For example:
With this input:
while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.

Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”

The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.

It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
The output should be:
[
("entity", "person", "Alex", "Alex is a character who experiences frustration and is observant of the dynamics among other characters."),
("entity", "person", "Taylor", "Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."),
("entity", "person", "Jordan", "Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."),
("entity", "person","Cruz","Cruz is associated with a vision of control and order, influencing the dynamics among other characters."),
("entity", "technology","The Device", "The Device is central to the story, with potential game-changing implications, and is revered by Taylor.")
("relationship", "Alex","Taylor","Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device.","power dynamics, perspective shift"),
("relationship","Alex","Jordan", "Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.","shared goals, rebellion"),
("relationship","Taylor","Jordan", "Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce.","conflict resolution, mutual respect"),
("relationship","Jordan","Cruz","Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order.","ideological conflict, rebellion"),
("relationship", "Taylor", "The Device", "Taylor shows reverence towards the device, indicating its importance and potential impact.","reverence, technological significance"),
]


This in the input text: {input_text}

"""

PROMPT["CHAT"] = """
You will be provided with a list of information. Your task is to accurately answer a question based solely on the information given.

Example:

Information:

The quick brown fox jumps over the lazy dog.
A dog is a domesticated animal.
Question:

What is a dog?
Your Response:

A dog is a domesticated animal.

Remember to:

Be specific: Clearly outline the task and any specific guidelines.
Provide context: If necessary, provide additional context or background information.
Set expectations: Clarify the desired format and level of detail in the response. Answer be the language in the question

Answer this question:
{question}

Information:
{received}
"""

PROMPT["RELATIONSHIP_POLLING"] = """
Do the following:
0. Don't write any code.
1. Get all the entities and find out it is a location, organization, person, geo or event, ....
2. Get all relationship of one entity to other entities from the input text. The relationship can be any thing from help, create, friend with, ...
3. Return it as in the format of ("entity", ..., ...  ) for the entity type or ("relationship", ..., ....) the relationship type. Don't give any empty output. It always started with either entity or a relationship 
4. Minimize amount of entities that don't have any relattionship.

Example output:
[
("entity", "person", "Alex", "Alex is a character who experiences frustration and is observant of the dynamics among other characters."),
("entity", "person", "Taylor", "Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."),
("relationship", "Alex","Taylor","Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device.","power dynamics, perspective shift"),
("relationship","Alex","Jordan", "Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.","shared goals, rebellion"),
("relationship", "Taylor", "The Device", "Taylor shows reverence towards the device, indicating its importance and potential impact.","reverence, technological significance"),
]


Will provide you a list of relationships can you find additional entities / relationships from that
This is the this of relationships
{relationships}

"""

PROMPT["ENTITY_POLLING"] = """
Do the following:
0. Don't write any code.
1. Get all the entities and find out it is a location, organization, person, geo or event, ....
2. Get all relationship of one entity to other entities from the input text. The relationship can be any thing from help, create, friend with, ...
3. Return it as in the format of ("entity", ..., ...  ) for the entity type or ("relationship", ..., ....) the relationship type. Don't give any empty output. It always started with either entity or a relationship 
4. Minimize amount of entities that don't have any relattionship.

Example output:
[
("entity", "person","Cruz","Cruz is associated with a vision of control and order, influencing the dynamics among other characters."),
("entity", "technology","The Device", "The Device is central to the story, with potential game-changing implications, and is revered by Taylor.")
("relationship", "Alex","Taylor","Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device.","power dynamics, perspective shift"),
("relationship","Alex","Jordan", "Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision.","shared goals, rebellion"),
]

Will provide you a list of entities can you find additional entities / relationships from that
This is the this of relationships
{entities}

"""

PROMPT["EXTRACT_ENTITY_CHAT"] = """
Do the following:
0. Don't write any code.
1. An entity is an noun which represent a location, organization, person, geo or event, .... Find all entities, that have that propertity.
2. If the quesiton is about location, organization, person, geo or event, .... 
3. Return the output of is either  ("entity", ...) or ("type", ... )

Example 1:

Question:

Who is Alex?

Output:
[
("entity", "person", "Alex"),
]

Example 2:

Question:

Tell me about any orginization in the document?

Output:
[
("type", "Orginization"),
]

This is the question:
{question}
"""

QUERY: dict[str, str] = {}

QUERY["entity"] = (
    'CREATE (c:`{type}` {{id: "{name}", description: "{description}" }}) RETURN c;\n'
)


QUERY["relationship"] = """
MATCH (e1 {{id: \"{e1}\"}}), (e2 {{id: \"{e2}\"}})
CREATE (e1)-[:`{relation}` {{ description: \"{description}\", keywords: \"{keywords}\" }} ]->(e2);
"""

QUERY["match"] = """
MATCH (e)-[r]-(e2)
WHERE e.id = "{id}"
RETURN e.description, r.description, e2.description LIMIT 120;
"""

QUERY['update'] = """
MATCH (e {{id: "{id}"}})
SET e.description = e.description + '. ' + "{description}";
"""

QUERY['update_edge'] = """
MATCH (e1 {{id: "{e1}"}})-[r:`{relation}`]->(e2 {{id: "e2"}})
SET r.description = r.description + '. ' + "{description}";
"""

QUERY["match_all"] = """
MATCH (n) RETURN DISTINCT n.id;
"""

QUERY["match_list"] = """
MATCH (e)-[r]-(e2)
WHERE e.id IN [{ids}]
RETURN DISTINCT e.description, r.description, e2.description LIMIT 120;
"""

QUERY["match_type"] = """
MATCH (n: `{type}`)-[r]-(e2) RETURN n.description, r.description, e2.description LIMIT 120;
"""

