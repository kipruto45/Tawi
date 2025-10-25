// Example: POST to /accounts/api/role_check/ using fetch with CSRF token
// Usage:
//  - Ensure the page includes the CSRF cookie (Django sets it when rendering forms)
//  - This example reads the CSRF token from the cookie and sends it in the X-CSRFToken header

function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

async function roleCheck(username, role) {
  const csrftoken = getCookie('csrftoken');
  const url = '/accounts/api/role_check/';
  const body = JSON.stringify({ username, role });

  const resp = await fetch(url, {
    method: 'POST',
    credentials: 'same-origin', // send cookies
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body
  });

  if (!resp.ok) {
    throw new Error('Network error: ' + resp.status);
  }
  return resp.json();
}

// Example usage from the browser console:
// roleCheck('alice', 'volunteer').then(console.log).catch(console.error)

// Note: the endpoint requires a valid CSRF token when called from browser
// pages that share the site's cookies. Use the pattern above (send
// X-CSRFToken and credentials:'same-origin') to avoid 403 responses.
