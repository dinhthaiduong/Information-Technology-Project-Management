QUERY: dict[str, str] = {}

QUERY["entity"] = (
    'create (c:`{type}` {{id: "{name}", description: "{description}" }}) return c;\n'
)


QUERY["relationship"] = """
match (e1 {{id: \"{e1}\"}}), (e2 {{id: \"{e2}\"}})
create (e1)-[:`{relation}` {{ description: \"{description}\", keywords: \"{keywords}\" }} ]->(e2);
"""

QUERY["match"] = """
match (e)-[r]-(e2)
where e.id = "{id}"
return e.description, r.description, e2.description limit 120;
"""

QUERY["update"] = """
match (e {{id: "{id}"}})
set e.description = e.description + '. ' + "{description}";
"""

QUERY["update_edge"] = """
match (e1 {{id: "{e1}"}})-[r:`{relation}`]->(e2 {{id: "e2"}})
set r.description = r.description + '. ' + "{description}";
"""

QUERY["match_all"] = """
match (n) return distinct n.id;
"""

QUERY["match_labels"] = """
match (n) unwind labels(n) as label return distinct label;
"""

QUERY["match_list"] = """
match (e)-[r]-(e2)
where e.id in [{ids}]
return distinct e, r, e2;
"""

QUERY["match_type"] = """
match (n: `{type}`)-[r]-(e2) return distinct n, r, e2;
"""
