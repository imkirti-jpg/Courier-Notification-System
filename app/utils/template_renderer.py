from jinja2 import Environment, TemplateSyntaxError

env = Environment()

def validate_template_syntax(body: str):
    try:
        env.parse(body)
    except TemplateSyntaxError as e:
        raise ValueError(f"Invalid Jinja2 syntax: {e}")

def render_template(body: str, context: dict) -> str:
    template = env.from_string(body)
    return template.render(**context)   