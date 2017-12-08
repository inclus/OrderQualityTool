var tests = require.context('./test-definition', true, /test\.js$/);

tests.keys().forEach(tests);

var components = require.context('./test-definition', true, /app\.js$/);

components.keys().forEach(components);