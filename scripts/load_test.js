import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp-up to 50 virtual users over 1 minute
    { duration: '3m', target: 50 },   // Stay at 50 virtual users for 3 minutes
    { duration: '1m', target: 200 },  // Ramp-up to 200 virtual users over 1 minute
    { duration: '3m', target: 200 },  // Stay at 200 virtual users for 3 minutes
    { duration: '1m', target: 0 },    // Ramp-down to 0 virtual users over 1 minute
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'], // 95% of requests must complete within 500ms
    'http_req_failed': ['rate<0.01'],   // Request failure rate must be less than 1%
  },
};

const API_GATEWAY_URL = __ENV.API_GATEWAY_URL || 'http://localhost:8080';

export default function () {
  // Generate unique email for this VU iteration
  const userEmail = `user-${__VU}-${__ITER}-${Date.now()}@test.com`;
  const userPassword = 'password123';

  // Simulate a user browsing products
  const productsRes = http.get(`${API_GATEWAY_URL}/products`);
  check(productsRes, { 'products page is status 200': (r) => r.status === 200 });
  sleep(1);

  // Simulate a user attempting to register
  const registerPayload = JSON.stringify({
    email: userEmail,
    password: userPassword,
  });
  const registerParams = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  const registerRes = http.post(`${API_GATEWAY_URL}/auth/register`, registerPayload, registerParams);
  check(registerRes, { 'register success': (r) => r.status === 201 || r.status === 409 });
  sleep(1);

  // Use the same email/password for login
  const loginPayload = JSON.stringify({
    email: userEmail,
    password: userPassword,
  });
  const loginRes = http.post(`${API_GATEWAY_URL}/auth/login`, loginPayload, { headers: { 'Content-Type': 'application/json' } });
  if (loginRes.status === 200 && loginRes.json('access_token')) {
    const accessToken = loginRes.json('access_token');
    const authHeaders = {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    };

    // Simulate an authenticated user viewing their orders
    const ordersRes = http.get(`${API_GATEWAY_URL}/orders/`, authHeaders);
    check(ordersRes, { 'orders page is status 200': (r) => r.status === 200 });
  }
  sleep(1);
}
