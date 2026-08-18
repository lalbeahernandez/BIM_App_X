import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
const datasetId = __ENV.DATASET_ID || 'tiny-health-smoke';
const gitCommit = __ENV.GIT_COMMIT || 'unknown';

export const options = {
  vus: Number(__ENV.K6_VUS || 5),
  duration: __ENV.K6_DURATION || '20s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<300'],
  },
  tags: {
    benchmark: 'api-health-smoke',
    dataset_id: datasetId,
    git_commit: gitCommit,
  },
};

export function setup() {
  return {
    baseUrl,
    datasetId,
    gitCommit,
    runTimestamp: new Date().toISOString(),
  };
}

export default function (metadata) {
  const response = http.get(`${metadata.baseUrl}/health`, {
    tags: { operation: 'GET /health' },
  });
  check(response, {
    'health 200': (r) => r.status === 200,
    'health body ok': (r) => r.body && r.body.includes('"status":"ok"'),
  });
  sleep(0.2);
}
