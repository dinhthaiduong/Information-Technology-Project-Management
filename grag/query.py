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

QUERY["update"] = """
MATCH (e {{id: "{id}"}})
SET e.description = e.description + '. ' + "{description}";
"""

QUERY["update_edge"] = """
MATCH (e1 {{id: "{e1}"}})-[r:`{relation}`]->(e2 {{id: "e2"}})
SET r.description = r.description + '. ' + "{description}";
"""

QUERY["match_all"] = """
MATCH (n) RETURN DISTINCT n.id;
"""

QUERY["match_list"] = """
MATCH (e)-[r]-(e2)
WHERE e.id IN [{ids}]
RETURN DISTINCT e.description, r.description, e2.description LIMIT 10;
"""

QUERY["match_type"] = """
MATCH (n: `{type}`)-[r]-(e2) RETURN DISTINCT n.description, r.description, e2.description LIMIT 10;
"""
