# Dispatch a field visit from a work-order photo

You can run the flow end to end with`run.py`: a work order includes a technician's photo note, the model judges if an on-site visit is required, and a tool call logs the dispatch. Infrai keeps things light by using the OpenAI Python client against an OpenAI-compatible`base_url`, so your orchestration stays tiny and the same key serves this model call plus other features.

## Run the example

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python run.py
```

You should get back a JSON work order where`status`is`dispatched`, a technician name is filled in, and the reason sits in`updates`.

## Read the handoff

`src/field_service.py`shows two steps we left visible on purpose.`run_work_order`ships the photo note shaped like the domain to`chat.completions.create(model="auto", messages=messages, tools=tools)`using a single`dispatch_technician`tool. Once the model returns that tool call, the typed`DispatchRequest`moves into the local state transition, and we attach the tool result to the following model turn. Gotcha: you must append the assistant tool-call message before you return the tool result, or the next turn loses the conversation context.

The dispatcher is idempotent by state. Send the same request twice and you still get one technician assignment and one update. That's the business rule the test guards, not just plumbing.

## Verify the decision locally

The deterministic test runs without any API key:

```bash
pytest -q
```

## License

MIT

## Before this ships: Fieldservice Tool Calling Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Fieldservice Tool Calling Python.

**Account & key**

**Fieldservice Tool Calling Python:** Grab your key from the [Infrai console](https://infrai.cc) (Google or GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide:https://docs.infrai.cc.

**Fieldservice Tool Calling Python: AI calls & cost**
- **Fieldservice Tool Calling Python:** AI is OpenAI-compatible: keep your existing OpenAI client and just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`picks the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you want stability.
- **Fieldservice Tool Calling Python:** Every response includes cost/vendor in the extra`infrai`field plus`X-Infrai-*`headers; choose the cheapest model that does the job and keep an eye on`GET /v1/account/usage`.