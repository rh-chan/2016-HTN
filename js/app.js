import React from 'react';
import ReactDOM from 'react-dom';
import _ from 'underscore';
import Spinner from 'react-spinner'

import SearchInput, {createFilter} from 'react-search-input'

const KEYS_TO_FILTERS = ['name']
var interval1;
var interval2;
var interval3;
//                  <p className="rating">Rating: {restaurant.rating}</p>
const Search = React.createClass({
  getInitialState: function() {
    return {
			searchTerm: '',
			searchResults: [],
      selectedRestaurants: []
		};
  },
  render: function() {
    return (
      <div>
        <SearchInput className="search-input" onChange={this.searchUpdated} onFocus={this.onFocus} />
				{this.state.focus ?
  				<div className="optionList">
  	        {this.state.searchResults.map(restaurant => {
  	          return (
  	            <div className="restaurant" data-id= {restaurant.id} key={restaurant.id} onClick={_.bind(this.selectRestaurant, this)}>
  	              <p className="name">{restaurant.name}</p>
  	              <p className="address">{restaurant.location_address[0]}</p>
  	            </div>
  	          )
  	        })}
  				</div> : null}
        <div className="container selectedContainer">
          <div className="row">
            <div className="selected chosenList col-xs-10 col-xs-offset-1">
              <div className="columnTitle">C H O I C E S</div>
              {this.state.selectedRestaurants.map(restaurant => {
                return (
                  <div className="chosenRestaurant" data-id= {restaurant.id} key={restaurant.id}>
                    <div className="right" data-id= {restaurant.id} onClick={_.bind(this.deleteRestaurant, this)}><span className="glyphicon glyphicon-remove-sign" aria-hidden="true"></span></div>
                    <p className="name">{restaurant.name}</p>
                    <p className="address">{restaurant.location_address[0]}</p>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    )
  },

  searchUpdated (term) {
		$.get("/yelp_search", {name: term, location: "waterloo"}, _.bind(function(data) {
			this.setState({searchResults: term.length > 0 ? JSON.parse(JSON.parse(data)) : [], searchTerm: term})
		}, this))
    this.setState({searchTerm: term})
  },
	onFocus (e) {
		this.setState({focus: true});
	},
  selectRestaurant (selectedRestaurant) {
    selectedRestaurant = $(selectedRestaurant.target);
    if ($(selectedRestaurant).attr('class') === "name" || $(selectedRestaurant).attr('class') === "address") {
      selectedRestaurant = $(selectedRestaurant).parent();
    }

    var currentRestaurants = this.state.selectedRestaurants;
    currentRestaurants.push(_.find(this.state.searchResults, function(restaurant) {return restaurant.id === selectedRestaurant.data("id")}))
    this.setState({selectedRestaurants: currentRestaurants, focus: false});
  },
  deleteRestaurant (deletedRestaurant) {
    deletedRestaurant = $(deletedRestaurant.target).parent();
    var id = deletedRestaurant.data('id');
    var selectedRestaurants = this.state.selectedRestaurants;
    selectedRestaurants = _.reject(selectedRestaurants, function(r) { return r.id == id});
    deletedRestaurant.parent().fadeOut(400, _.bind(function() {
      this.setState({selectedRestaurants: selectedRestaurants});
    }, this));
  }
})

          //<h1> Current Step: {this.state.step} </h1>
var App = React.createClass({
	getInitialState: function() {
    return {
			step: 'name',
			restaurants: [],
      name: "",
      roomId: "",
      doneSubmitting:[],
      votedIndex: 0,
      winner: null
		};
  },
  render: function() {
    if (this.state.step === 'name') {
      return (
        <div className="center">
          <form>
            <div className="form-group">
              <label htmlFor="nameInput">Enter your name:</label>
              <input id="nameInput" type="text"/>
              <button type="button" className="btn btn-primary" onClick={this.handleName}>start</button>
            </div>
          </form>
        </div>
      )
    }
		else if (this.state.step === 'create') {
			return (
				<div className="center">
					<button type="button" className="btn btn-primary" onClick={this.handleCreated}>create choosr poll</button>
					<button type="button" className="btn btn-info" onClick={this.gotoCreated}>join existing choosr</button>
				</div>
			);
		}
    else if (this.state.step === "join") {
      return (
        <div className="center">
          <form>
            <div className="form-group">
              <label htmlFor="roomInput">Enter room number:</label>
              <input id="roomInput" type="text"/>
              <button type="button" className="btn btn-primary join-btn" onClick={this.handleJoin}>join</button>
            </div>
          </form>
        </div>
      )
    }
		else if (this.state.step === 'add') {
			return (
				<div className="center">
        	<p className="center roomNumber"> Hi {this.state.name}, your room code is : {this.state.roomId} </p>
					<Search ref="search"/>
          <div className="center">
          	<button type="button" className="btn btn-success" onClick={this.doneSubmitting}>finish</button>
          </div>

      	</div>)
		}
    else if (this.state.step === 'waiting') {
      return (
        <div className="center">
          <p className="center roomNumber"> Hi {this.state.name}, your room code is : {this.state.roomId} </p>
          <p className="center title"> Friends that have submitted their suggestions: </p>
          <div className="container selectedContainer submittedContainer">
            <div className="row">
              <div className="selected votedPerson col-xs-10 col-xs-offset-1">
                {_.map(this.state.doneSubmitting, person => {
                  return (
                    <div className="submittedPerson" data-id={person} key={person}>
                      <p className="name">{person}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
          <button type="button" className="btn btn-success" onClick={this.startVoting}>start voting</button>
        </div>
      )
    }
    else if (this.state.step === 'voting') {
      var restaurant = this.state.restaurants[this.state.votedIndex];
      return (
        <div className="center">
              <div className="selected votedRestaurant">
                <div className="submittedPerson" data-id={restaurant.suggestion} key={restaurant.suggestion_name}>
                  <p className="name">{restaurant.suggestion_name}</p>
                  <p className="location">{restaurant.address}</p>
                  <p className="rating">Rating on Yelp: {restaurant.rating}</p>
                  <button type="button" className="btn btn-success" data-id={restaurant.suggestion} data-rank="2" onClick={this.vote}>so down</button>
                  <button type="button" className="btn btn-info" data-id={restaurant.suggestion} data-rank="1" onClick={this.vote}>meh</button>
                  <button type="button" className="btn btn-warning"data-id={restaurant.suggestion} data-rank="0" onClick={this.vote}>nah</button>
                </div>
              </div>
        </div>
      )
    }
    else if (this.state.step === 'votingwaiting') {
      return (
        <div className="center">
          <p className="center title"> You're done voting! Now we're waiting for your friends to submit their votes. </p>
          <Spinner />
        </div>
    )
    }
    else if (this.state.step === 'result') {
      return (
        <div className="center">
          <div className="firstResult">
          <h1>W I N N E R</h1>
          <p>{this.state.winner.suggestion_name} </p>
          <p className="address"> {this.state.winner.address} </p>
          <p> Rating of {this.state.winner.rating} on Yelp</p>
          </div>
        </div>
      )
    }
  },
  vote: function(e) {
    $.post("/suggestion_vote", {rank: $(e.target).data("rank"), suggestion: $(e.target).data("id"), user_id: this.state.userId}, _.bind(function(data) {
      var newIndex = this.state.votedIndex + 1;
      if (newIndex >= this.state.restaurants.length) {
        this.setState({step: 'votingwaiting'});
        $.post("/voting_end", {user_id: this.state.userId});
        interval3 = setInterval(_.bind(this.checkVotingEnd, this), 1000);
      }
      else {
        this.setState({votedIndex: newIndex});
      }
    }, this))
  },
  checkVotingEnd: function(e) {
    $.get("/check_room_votes", {room_id: this.state.roomId}, _.bind(function(data) {
      if (JSON.parse(data)==true) {
        clearInterval(interval3);
        $.get("/rank_algo", {room_id: this.state.roomId}, _.bind(function(data) {
          var winner = JSON.parse(data)[0][0];
          winner = _.find(this.state.restaurants, _.bind(function(restaurant) {
            return (restaurant.suggestion == winner);
          }, this))
          this.setState({step: "result", winner: winner});
        }, this))
      }
    }, this));
  },
  startVoting: function() {
    $.get("/update_room_status", {room_id: this.state.roomId}, _.bind(function(data) {
      clearInterval(interval1);
      clearInterval(interval2);
      this.getAllSuggestions();
      this.setState({step: "voting"});
    }, this));
  },
  handleName: function(form) {
    this.setState({step: "create", name: $("#nameInput").val()});
  },
  gotoCreated: function() {
    this.setState({step: 'join'});
  },
  handleJoin: function() {
    $.post("/user", {name: this.state.name, room_id: $("#roomInput").val()}, _.bind(function(data) {
      this.setState({roomId: $("#roomInput").val(), step: "add", userId: data});
    }, this));
    $('.middleLogo').animate({
      marginTop: "5em"
    }, 500, function() {

    });
  },
  handleCreated: function() {
    $.post("/room", {name: this.state.name, room_name: "paninos"}, _.bind(function(data) {
      data = JSON.parse(data);
      this.setState({roomId: data.room_id, userId: data.user_id});
		}, this));
		$('.middleLogo').animate({
			marginTop: "5em"
		}, 500, function() {
			// animation complete callback
		});
    this.setState({step: "add"});
  },
  doneSubmitting: function() {
    $.post("/suggestions", {suggestions: JSON.stringify(this.refs.search.state.selectedRestaurants), room_id: this.state.roomId, user_id: this.state.userId}, _.bind(function(data) {
      this.setState({step: "waiting"});
    }, this));
    interval1 = setInterval(_.bind(this.checkWhosDone, this), 1000);
    interval2 = setInterval(_.bind(this.checkIfStartVote, this), 1000);
  },
  checkWhosDone: function() {
    $.get("/room_submitted", {room_id: this.state.roomId}, _.bind(function(data) {
      this.setState({doneSubmitting: JSON.parse(data)});
    }, this));
  },
  checkIfStartVote: function() {
    $.get("/room", {room_id: this.state.roomId}, _.bind(function(data) {
      if (JSON.parse(data) == 2) {
        clearInterval(interval1);
        clearInterval(interval2);
        this.getAllSuggestions();
        this.setState({step: "voting"});
      }
    }, this));
  },
  getAllSuggestions: function() {
    $.get("/suggestions", {room_id: this.state.roomId}, _.bind(function(data) {
      this.setState({restaurants: JSON.parse(data)});
    }, this));
  }
});

var Dropdown = React.createClass({
	render: function() {
		return (
			<div className="center">
		</div>
		)
	}
});

/*
{_.map(this.props.data, function(restaurant) {
	return (
		<div>{restaurant.name}</div>
	)
})}*/


ReactDOM.render(
  <App/>,
  document.getElementById('main')
);
