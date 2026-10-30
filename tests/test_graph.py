from builder.graph import build_graph


def _chunk(topic, modules, learning):
    return {"modules": [{"id": m, "title": m.upper()} for m in modules], "learning": learning}


def test_build_graph_edges_and_layout():
    chunks = {
        "quant": _chunk("quant", ["m01.1", "m01.2", "m01.3"], {
            "m01.2": {"connections": [{"to": "m01.1", "type": "requires", "note": "n1"},
                                      {"to": "m99.9", "type": "requires", "note": "unknown module"},
                                      {"to": "m01.2", "type": "extends", "note": "self loop"}]},
        }),
        "fi": _chunk("fi", ["m23.1"], {"m23.1": {"connections": [{"to": "m01.2", "type": "applies", "note": "n2"}]}}),
    }
    g = build_graph(chunks, ["quant", "fi"])
    assert g["edges"] == [{"from": "m01.2", "to": "m01.1", "type": "requires", "note": "n1"},
                          {"from": "m23.1", "to": "m01.2", "type": "applies", "note": "n2"}]
    # Only connected modules are drawn; positions are normalised to 0..1
    assert [n["id"] for n in g["nodes"]] == ["m01.1", "m01.2", "m23.1"]
    assert {n["topic"] for n in g["nodes"]} == {"quant", "fi"}
    assert all(0 <= n["x"] <= 1 and 0 <= n["y"] <= 1 for n in g["nodes"])
    assert build_graph(chunks, ["quant", "fi"]) == g  # deterministic, so the content hash is stable


def test_build_graph_without_connections_is_none():
    assert build_graph({"quant": _chunk("quant", ["m01.1"], {"m01.1": {}})}, ["quant"]) is None
