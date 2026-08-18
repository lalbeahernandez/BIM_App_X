import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = { vus: 5, duration: '20s' };
export default function () {
  const res = http.get('http://localhost:8000/health');
  check(res, { 'health 200': r => r.status === 200 });
  sleep(0.2);
}
