function(request, state, logger, callback) {

  if (typeof state.schema === "undefined") {
    var response = {
      statusCode: 404,
      body: {
        "error": "No JSON Schema found - have you POSTed it yet?"
      }
    };
    callback(response);
  }

  if (request.query['all'] === "true") {
    var fakeAll = true;
  }
  else {
    var fakeAll = false;
  }

  const jsf = require("json-schema-faker");

  jsf.option({
    alwaysFakeOptionals: fakeAll
  });

  jsf.resolve(state.schema).then(function(sample) {
    var response = {
        statusCode: 200,
        body: JSON.stringify(sample, null, 4)
    };
    callback(response);
  });
}