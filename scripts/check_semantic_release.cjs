const assert = require('node:assert/strict');
const {analyzeCommits} = require('@semantic-release/commit-analyzer');
(async () => {
  for (const [message, expected] of [['fix: repair transfer', 'patch'], ['feat: add transfer', 'minor'], ['feat!: change imports', 'major'], ['docs: improve manual', null]]) {
    const result = await analyzeCommits({preset: 'conventionalcommits'}, {
      cwd: process.cwd(), commits: [{message, hash: 'test'}], logger: {log() {}}
    });
    assert.equal(result, expected, message);
  }
  console.log('Conventional Commit patch/minor/major and non-release behavior verified');
})().catch(error => { console.error(error); process.exitCode = 1; });
