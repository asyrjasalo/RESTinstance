function(request, state, logger, callback) {

  const proxy = require(`${process.cwd()}/testapi/responders/proxy.js`);

  proxy.fetch_response(request, state, logger, response => {
    if (response.statusCode != 200 && response.statusCode != 201) {
      response = {
        statusCode: 404,
        body: { "error": "Not found" }
      }
    }
    else {
      const token = response.token;
      response = {
        statusCode: 204,
        body: response.body
      }
      state.instances[token].responses[request.path] = response;
    }
    callback(response);
  });

}
