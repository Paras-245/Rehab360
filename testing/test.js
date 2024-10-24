// Example login function
async function login(username, password) {
    const response = await fetch('http://localhost:8000/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
    });

    const data = await response.json();

    if (response.ok) {
        // Store tokens in localStorage
        console.log('Login successful:', data);
        // localStorage.setItem('access_token', data.access);
        // localStorage.setItem('refresh_token', data.refresh);
    } else {
        console.error('Login failed:', data);
    }
}

// Example protected API call function
async function fetchProtectedData() {
    // const accessToken = localStorage.getItem('access_token');
    const accessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5NzkzNTQ1LCJpYXQiOjE3Mjk3OTMyNDUsImp0aSI6ImZlMTQ4NDg2YzBiYzQ3OTFhNmZmNWE4YjAyOTUwMjI4IiwidXNlcl9pZCI6Mn0.BIHPKPHz6zSdXWBmue6Q7162_mz4WnMT3TN7LkCyQEE'


    const response = await fetch('http://localhost:8000/api/protected-route/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
        },
    });

    if (response.ok) {
        const data = await response.json();
        console.log('Protected data:', data);
    } else {
        console.error('Failed to fetch protected data:', response.status);
    }
}


fetchProtectedData();