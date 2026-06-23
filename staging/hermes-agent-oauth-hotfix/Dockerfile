FROM sarl/hermes-agent:uid10010

USER root
COPY --chown=hermes:hermes anthropic_adapter.py /opt/hermes/agent/anthropic_adapter.py
RUN python -m py_compile /opt/hermes/agent/anthropic_adapter.py
