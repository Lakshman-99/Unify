import React from 'react';
import { ChatContext } from './App.js';

function LoginForm() {
  const chatData  = React.useContext(ChatContext);
  const userInput = React.useRef();
  const [error, setError] = React.useState(false);
  const login = (ev) => {
    if (ev.type === 'keyup' && ev.key !== 'Enter') {
      return;
    }
    setError(false);
    chatData.login(userInput.current.value).catch(() => setError(true));
  }
  const logout = () => chatData.logout();

  if (chatData.user.username === null) {
    return (
    <div class="minn">
      <div class="nan">

      </div>
      <div id="login">


          Username:&nbsp;

          <input type="text" div="mll" ref={userInput} onKeyUp={login} autoFocus />
          &nbsp;
          <button class="but"onClick={login}>Login </button>
          {error && <>&nbsp;Login error, please try again.</>}

        </div>

</div>
    );
  }
  else {
    return (
      <div id="login">
        <div class="out">
          Username: <b>{ chatData.user.username }</b>&nbsp;
          <button class="but" onClick={logout}>Logout</button>
        </div>
      </div>
    );
  }
}

export default LoginForm;
