from mail_helper import TemplateHelper


def test_template_helper_renders_context_and_globals(tmp_path):
    (tmp_path / "welcome.html").write_text("<p>{{ app_name }} {{ name }}</p>")
    helper = TemplateHelper(str(tmp_path), globals={"app_name": "Mail"})

    assert helper.render("welcome.html", {"name": "Ada"}) == "<p>Mail Ada</p>"


def test_template_helper_autoescapes_html(tmp_path):
    (tmp_path / "welcome.html").write_text("<p>{{ name }}</p>")
    helper = TemplateHelper(str(tmp_path))

    assert helper.render("welcome.html", name="<Ada>") == "<p>&lt;Ada&gt;</p>"
