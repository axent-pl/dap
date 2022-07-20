import React, { Component } from 'react';
import ListGroup from 'react-bootstrap/ListGroup';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import './App.css';
import Plot from 'react-plotly.js';

class DatasetObserver {
  static selectHandlers = []
  static changeHandlers = []

  static subscribeChanged(fn) {
    DatasetObserver.changeHandlers.push(fn)
  }

  static notifyChanged(dataset) {
    DatasetObserver.changeHandlers.forEach((handler) => {
      handler(dataset)
    })
  }

  static subscribeSelected(fn) {
    DatasetObserver.selectHandlers.push(fn)
  }

  static notifySelected(dataset) {
    DatasetObserver.selectHandlers.forEach((handler) => {
      handler(dataset)
    })
  }

}

class DatasetListItem extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      isSelected: false,
      dataset: props['dataset']
    };
  }

  render = () => {
    return (
      <ListGroup.Item key="{this.state.dataset.name}" className={this.state.isSelected ? "active" : ""}>{this.state.dataset.name}</ListGroup.Item>
    )
  }
}

class DatasetList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      items: []
    };
  }

  componentDidMount() {
    fetch(this.props['uri'])
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            items: result
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render = () => {
    return (
      <Card>
        <Card.Body>
          <Card.Title>Datasets</Card.Title>
          <ListGroup>
              { this.state.items.map(item => (<DatasetListItem key={item.name} dataset={item} />)) }
          </ListGroup>
        </Card.Body>
      </Card>);
  }
}

class App extends Component {
  render = () => {
    return (
      <div>
        <DatasetList uri="/api/datastore/dataset" />
      <Plot
        data={[
          {
            x: [1, 2, 3],
            y: [2, 6, 3],
            type: 'scatter',
            mode: 'lines+markers',
            marker: {color: 'red'},
          },
          {type: 'bar', x: [1, 2, 3], y: [2, 5, 3]},
        ]}
        layout={{title: 'A Fancy Plot'}}
      />
      </div>
    );
  }
}

export default App;
