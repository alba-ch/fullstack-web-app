<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg pt-1">
      <div class="container text-center">
        <a class="navbar-brand text-center mx-auto" href="#"><i>SPORTALIA</i></a>
      </div>
    </nav>
    <div class="container mx-auto justify-content-center mt-5">
      <div class="row mt-5 pt-5">
        <div v-if="creatingAccount" class="card mx-auto col-5 p-4">
          <h3 class="mb-4">Create an account</h3>
          <form>
            <div class="form-label-group">
              <label for="inputEmail">Username</label>
              <input type="username" id="inputUsername" class="form-control" placeholder="Username" required autofocus
                v-model="addUserForm.username">
            </div>
            <div class="form-label-group">
              <br>
              <label for="inputPassword">Password</label>
              <input type="password" id="inputPassword" class="form-control" placeholder="Password" required
                v-model="addUserForm.password">
            </div>
            <div class="text-center">
              <button type="submit" class="btn btn-primary w-100 d-block mt-4" @click="onSubmit">Submit</button>
              <button class="btn btn-outline-success w-100 d-block mt-3" @click="backToLogin">Back To Log In</button>
            </div>
          </form>
        </div>
        <!-- SIGN IN -->
        <div v-else class="card mx-auto col-5 p-4">
            <h3 class="mb-4">Sign In</h3>
            <div class="form-label-group">
              <label for="inputEmail">Username</label>
              <input type="username" id="inputUsername" class="form-control"
              placeholder="Username" required autofocus v-model="username">
            </div>
            <div class="form-label-group">
              <br>
              <label for="inputPassword">Password</label>
              <input type="password" id="inputPassword" class="form-control"
              placeholder="Password" required v-model="password">
            </div>
            <div class="text-center">
              <button class="btn btn-primary w-100 d-block mt-4" @click="checkLogin">Sign In</button>
              <button class="btn btn-success w-100 d-block mt-3" @click="initCreateForm">Create Account</button>
              <button class="btn btn-outline-success w-100 d-block mt-3" @click="backToMatches">Back to Matches</button>
            </div>
        </div>
      </div>
     </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Login',
  data () {
    return {
      logged: false,
      username: null,
      password: null,
      token: null,
      creatingAccount: false,
      addUserForm: {
        username: null,
        password: null
      }
    }
  },
  methods: {
    checkLogin () {
      const parameters = 'username=' + this.username + '&password=' + this.password
      const path = 'http://localhost:8000/login'
      const config = {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      }
      axios.post(path, parameters, config)
        .then((res) => {
          this.logged = true
          this.token = res.data.access_token
          this.$router.push({ path: '/', query: { username: this.username, logged: this.logged, token: this.token } })
        })
        .catch((error) => {
          // eslint-disable-next-line
          alert('Username: ' + parameters.username + ' Password: ' + parameters.password)
          console.error(error)
          alert('Username or Password incorrect')
          // this.backToLogin()
        })
    },
    initCreateForm () {
      this.creatingAccount = true
      this.addUserForm.username = null
      this.addUserForm.password = null
    },
    onSubmit () {
      const parameters = {
        username: this.addUserForm.username,
        password: this.addUserForm.password
      }
      const path = 'http://localhost:8000/account'
      axios.post(path, parameters)
        .then((res) => {
          alert('Account created')
          this.backToLogin()
        })
        .catch((error) => {
          // eslint-disable-next-line
          alert('Username already exists')
          console.error(error)
        })
    },
    backToLogin () {
      this.creatingAccount = false
      this.username = null
      this.password = null
    },
    backToMatches () {
      this.$router.push({ path: '/' })
    },
    created () {
      this.backToLogin()
    }
  }
}
</script>

<style scoped>
#app {
  background-image: url('../assets/background.jpg');
  height: 100vh;
}
  .navbar {
    background-color: #000000;
    margin: 0;
    width: 100%;
  }
  .navbar-brand {
    color: #00ff15;
    font-size: 1.4rem;
  }
  .card {
    background-color: #000000c6;
    border: none;
    color: white;
    border-radius: 10px;
  }
  .form-label-group {
    margin-bottom: 1em;
  }
  .form-label-group > input {
    border: 1px solid #00ff15;
  }
</style>

