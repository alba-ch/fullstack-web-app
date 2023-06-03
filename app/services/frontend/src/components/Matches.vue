<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg">
      <div class="container justify-content-between mt-1">
        <a class="navbar-brand" href="#"><i>SPORTALIA</i></a>
        <div class="d-inline">
          <p v-if="logged === true" class="mr-3 d-inline">🧞‍♂️ {{ username }}</p>
          <p v-if="logged === true" class="mr-3 d-inline">💰 {{parseFloat(money_available).toFixed(2)}} &euro;</p>
          <button v-if="logged === false" class="btn btn-outline-success my-2 my-sm-0" @click="login">Log In</button>
          <button v-if="is_showing_cart" class="btn btn-outline-success my-2 my-sm-0" @click="showingCart">Tanca cistella</button>
          <button v-else class="btn btn-outline-success my-2 my-sm-0" @click="showingCart" :disabled="logged === false">Veure cistella <span class="badge badge-pill badge-success">{{ matches_added.length }}</span></button>
          <button v-if="logged === true" class="btn btn-outline-success my-2 my-sm-0" @click="logout">Log Out</button>
        </div>
      </div>
    </nav>
    <div v-if="is_showing_cart === false" class="container-fluid m-0 p-0">
      <div class="row m-0 p-0">
        <div class="col-12 m-0 p-0" id="full-banner">
          <div class="col-12 m-0 p-0 position-absolute" id="full-banner">
            <h3 class="my-auto mx-auto text-white" style="padding-top: 4em; font-size: 3rem;">SPORT MATCHES</h3>
            <h5 class="my-auto mx-auto text-white opacity-75" style="font-size: 1.5rem;">Buy your tickets now!</h5>
          </div>
          <img src="@/assets/banner3.jpg" alt="banner" id="banner"  class="img-fluid w-100 m-0 p-0">
        </div>
      </div>
      <div class="row mb-2">
        <div class="col-12 text-center" id="total-matches">
          <h5 class="p-4">{{ matches.length }} matches available</h5>
        </div>
      </div>
    </div>
    <div v-if="is_showing_cart" id="cistella" class="container mt-5 mx-auto">
      <div class="row">
        <div class="col-md-12">
          <table v-if="matches_added.length>0" class="table mx-auto">
            <thead class="mx-auto">
              <tr>
                <th>Sport</th>
                <th>Competition</th>
                <th>Match</th>
                <th>Quantity</th>
                <th>Price(&euro;)</th>
                <th>Total</th>
                <th></th>
              </tr>
            </thead>
            <tbody class="mx-auto">
              <tr v-for="(match,index) in matches_added" :key="match.id">
                <td>{{ match.match.competition.sport }}</td>
                <td>{{ match.match.competition.name }}</td>
                <td>{{ match.match.local.name }} vs {{ match.match.visitor.name }}</td>
                <td>
                  {{ match.ticket_count }}
                  <button class="btn btn-success" :disabled="(money_available) < (match.match.price + total_tickets_cost) || match.match.total_available_tickets<1" @click="addTicketFromMatch(index)">+</button>
                  <button class="btn btn-danger" :disabled="match.ticket_count==0" @click="returnTicketFromMatch(index)">-</button>
                </td>
                <td>{{ match.match.price }}</td>
                <td>{{ parseFloat(match.match.price * match.ticket_count).toFixed(2)}}</td>
                <td>
                  <button class="btn btn-danger" @click="removeMatch(index)">Eliminar entrada</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-center mx-auto">
            <h3>Cart</h3>
            <h5>Your cart is currently empty.</h5>
          </div>
          <div class="container mt-4 mx-auto">
            <button class="btn gray" @click="clearAllBasket">Buida cistella</button>
            <button class="btn btn-success" :disabled="matches_added.length==0" @click="finalizePurchase">Finalitzar compra</button>
          </div>
        </div>
      </div>
    </div>
    <div v-else id="partits" class="container mt-5">
      <div class="row">
        <div class="card col-lg-3 col-md-5 mb-4 mx-auto p-0" v-for="(match) in matches" :key="match.id" style="border-radius: 10px;">
          <img class="card-img-top" :src="require('@/assets/match' + match.id + '.jpg')" alt="Card image cap">
          <br>
          <div class="p-2 pb-0 mb-0">
              <h5 class="font-weight-bold">{{ match.competition.sport }} - {{ match.competition.category }}</h5>
            <h6>{{ match.competition.name }}</h6>
            <h6><strong>{{ match.local.name }}</strong> ({{ match.local.country }}) vs <strong>{{ match.visitor.name
            }}</strong> ({{ match.visitor.country }})</h6>
            <h6>{{ match.date.substring(0, 10) }}</h6>
            <h6>{{ match.price }} &euro;</h6>
            <h6 style="color: red;" class="mt-1">Only {{ match.total_available_tickets }} tickets left!</h6>
            <button class="btn btn-success mb-2 mx-2 mt-1" @click="addEventToCart(match)" :disabled="logged === false || match.total_available_tickets <= 0">Afegeix a la cistella</button>
          </div>
          <p v-if="logged === false" style="color: rgba(0, 0, 0, 0.697);" class="p-2">Has d'estar loguejat per poder comprar entrades</p>
        </div>
      </div>
    </div>
  </div>
</template>

<!-- Script correspon al codi JavaScript-->
<script>
import axios from 'axios'

export default {
  data () {
    return {
      is_showing_cart: false,
      matches_added: [],
      matches: [],
      total_tickets_cost: 0,

      logged: false,
      username: 'test',
      token: '',
      is_admin: false,
      money_available: 0
    }
  },
  methods: {
    getAccount () {
      const path = 'http://localhost:8000/account/' + this.username
      const config = {
        headers: { Authorization: 'Bearer ' + this.token }
      }

      axios.get(path, config)
        .then(res => {
          this.is_admin = res.data.is_admin
          this.money_available = res.data.available_money
        })
        .catch(error => {
          alert(error)
          console.log(error)
        })
    },
    login () {
      this.$router.push('/userlogin')
    },
    logout () {
      this.logged = false
      this.username = 'test'
      this.token = ''
      this.is_admin = false
      this.$router.push('/')
    },
    showingCart () {
      this.is_showing_cart = !this.is_showing_cart
      this.getMatches()
    },
    addEventToCart (match) {
      let exists = false
      for (let i = 0; i < this.matches_added.length; i += 1) {
        if (this.matches_added[i].match.id === match.id) {
          exists = true
        }
      }
      if (!exists) {
        this.matches_added.push({
          match: match,
          ticket_count: 0
        })
      }
    },
    removeMatch (index) {
      this.matches_added.splice(index, 1)
    },
    addTicketFromMatch (index) {
      this.matches_added[index].match.total_available_tickets -= 1
      this.matches_added[index].ticket_count += 1
      this.total_tickets_cost += this.matches_added[index].match.price
      console.log('Added ticket')
    },
    returnTicketFromMatch (index) {
      this.matches_added[index].match.total_available_tickets += 1
      this.matches_added[index].ticket_count -= 1
      this.total_tickets_cost -= this.matches_added[index].match.price
      console.log('Deleted ticket')
    },
    finalizePurchase () {
      for (let i = 0; i < this.matches_added.length; i += 1) {
        const parameters = {
          match_id: this.matches_added[i].match.id,
          tickets_bought: this.matches_added[i].ticket_count
        }
        console.log(parameters.match_id)
        console.log(parameters.tickets_bought)
        let index = i
        if (this.matches_added[i].ticket_count > 0) {

          this.addPurchase(parameters, i, this.matches_added[index].match)
        }
      }
    },
    addPurchase (parameters, index, match) {
      const path = 'http://localhost:8000/order/' + this.username
      const config = {
        headers: { Authorization: 'Bearer ' + this.token }
      }
      axios.post(path, parameters, config)
        .then(() => {
          this.money_available -= match.price * parameters.tickets_bought
          this.total_tickets_cost -= match.price * parameters.tickets_bought
          this.clearBasket(match.id)
          console.log('Order done')
        })
        .catch((error) => {
          // eslint-disable-next-line
          // alert('Error: ' + error.response.data.message)
          console.log(error)
        })
    },
    clearBasket (matchId) {
      for (let i = 0; i < this.matches_added.length; i += 1) {
        if (this.matches_added[i].match.id === matchId) {
          this.matches_added.splice(i, 1)
          // this.tickets_bought[matchId - 1]= 0
        }
      }
    },
    clearAllBasket () {
      this.matches_added = []
    },
    getMatches () {
      const pathMatches = 'http://localhost:8000/matches/'
      const pathCompetition = 'http://localhost:8000/competition/'

      axios.get(pathMatches)
        .then((res) => {
          var matches = res.data.filter((match) => {
            return match.competition.id != null
          })
          var promises = []
          for (let i = 0; i < matches.length; i++) {
            const promise = axios.get(pathCompetition + matches[i].competition.name)
              .then((resCompetition) => {
                delete matches[i].competition
                matches[i].competition = {
                  'name': resCompetition.data.name,
                  'category': resCompetition.data.category,
                  'sport': resCompetition.data.sport
                }
              })
              .catch((error) => {
                console.error(error)
              })
            console.log('Pushed promise: ')
            promises.push(promise)
          }
          Promise.all(promises).then((_) => {
            console.log(matches)
            this.matches = matches
          })
        })
        .catch((error) => {
          console.error(error)
        })
    }
  },
  created () {
    this.getMatches() // Carreguem els partits

    this.logged = this.$route.query.logged === 'true'
    this.username = this.$route.query.username
    this.token = this.$route.query.token

    if (this.logged === undefined || this.logged === false) {
      this.logged = false
    } else { this.getAccount() }
  }
}

</script>

<style scoped>
    #app{
      background-color: #fbfbfb;
    }
    #banner {
      margin: 0em;
      width: max-content;
      max-height: 40vh;
    }
    .container {
      margin-top: 20px;
    }
    .navbar {
      background-color: #000000;
      margin: 0;
      width: 100%;
    }
    .navbar-brand {
      color: #00ff15;
      font-size: 1.4rem;
      margin-left: 1em;
    }

    .navbar button {
      color: #00ff15;
      border-radius: 10px;
      font-size: 1rem;
      margin-left: 1em;
    }

    .navbar button:hover {
      color: #ffffff;
    }

    .navbar button:focus {
      outline: palegreen;
    }

    .full-banner {
      background-color: #000000;
    }

    #total-matches {
      background-color: #000000;
      color: rgba(0, 255, 34, 0.644);
      font-size: 1.2rem;
      font-weight: lighter;
    }

    .card {
      border-radius: 10px;
      width: 35em;
      border: none;
      box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.75);
    }

    .card:hover {
      transform: scale(1.05);
      transition: 0.5s;
    }

    .card button {
      width: fit-content;
      border-radius: 0px;
      background-color: #181818;
      color: #00ff15;
      font-size: 1rem;
      margin-left: 1em;
    }

    .card button:hover {
      color: #ffffff;
      background-color: #00920c;
    }

    .card img {
      border-radius: 10px 10px 0px 0px;
    }
</style>
