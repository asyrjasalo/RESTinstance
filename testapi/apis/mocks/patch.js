function(request, state, logger, callback) {

  if (!request.body) return {};

  var params = JSON.parse(request.body);
  if (params.id) {
    return {
      body: { "error": "Updating read-only parameter not allowed" }
    }
  }
  else if (Object.keys(params).length > 1) {
    return {
      body: { "error": "Updating multiple params not allowed" }
    }
  }

  const proxy = require(`${process.cwd()}/apis/mocks/proxy.js`);

  proxy.fetch_response(request, state, logger, response => {
    if (response.statusCode != 200 && response.statusCode != 201) {
      response = {
        statusCode: 404,
        body: { "error": "Not found" }
      }
    }
    else {
      var body = JSON.parse(response.body);
      var property = Object.keys(params)[0];
      if (body[property]) {
        body[property] = params[property];
        response = {
          statusCode: 200,
          body: JSON.stringify(body)
        }
        state.responses[request.path] = response;
      }
      else {
        response = {
          body: { "error": "Cannot change property that does not exist" }
        }
      }
    }
    callback(response);
  });

}
