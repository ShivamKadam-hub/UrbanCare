import axios from 'axios';

async function testFlow() {
  const api = axios.create({ baseURL: 'http://localhost:8000/api' });
  const email = 'test_flow@example.com';
  const password = 'mySecretPassword!12';

  try {
    // 1. Register
    console.log("Registering...");
    const regRes = await api.post('/auth/register', {
      name: 'Test Flow',
      email,
      password,
      role: 'customer'
    });
    console.log("Registered:", regRes.data.email);

  } catch (err) {
    if (err.response?.data?.detail !== 'Email already registered') {
        console.error("Register Error:", err.response?.data || err.message);
        return;
    }
    console.log("Already registered");
  }

  try {
    // 2. Login
    console.log("Logging in...");
    const loginRes = await api.post('/auth/login', {
      email,
      password
    });
    console.log("Login Token:", loginRes.data.access_token);
  } catch (err) {
    console.error("Login Error:", err.response?.data || err.message);
  }
}

testFlow();
