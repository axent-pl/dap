import React, { Component } from 'react';
import ListGroup from 'react-bootstrap/ListGroup';
import Card from 'react-bootstrap/Card';
import Tab from 'react-bootstrap/Tab';
import Tabs from 'react-bootstrap/Tabs';
import Table from 'react-bootstrap/Table';

import './App.css';
import Plot from 'react-plotly.js';

//---------------------------------------------------------------------------//

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

//---------------------------------------------------------------------------//

class DatasetList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      selectedDataset: null,
      datasets: []
    };
  }

  componentDidMount() {
    fetch(this.props['url'])
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            datasets: result
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

  handleSelect = (dataset) => {
    this.setState({
      selectedDataset: dataset.name
    })
    DatasetObserver.notifySelected(dataset)
  }

  render = () => {
    return (
      <Card>
        <Card.Body>
          <Card.Title>Datasets</Card.Title>
          <ListGroup>
              { this.state.datasets.map(dataset => (
                <ListGroup.Item key={dataset.name} className={(dataset.name == this.state.selectedDataset) ? "active" : ""} onClick={() => {this.handleSelect(dataset)}}>{dataset.name}</ListGroup.Item>
              )) }
          </ListGroup>
        </Card.Body>
      </Card>);
  }
}

//---------------------------------------------------------------------------//

class DatasetVariantList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      dataset: null,
      variants: []
    };
    DatasetObserver.subscribeSelected(this.handleDatasetSelected.bind(this));
  }  

  handleDatasetSelected = (dataset) => {
    fetch(dataset.variants_url)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            dataset: dataset,
            variants: result
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            dataset: null,
            variant: [],
            error
          });
        }
      )
  }

  render = () => {
    return (
      <Card>
        <Card.Body>
          <Card.Title>Variants</Card.Title>
          <Tabs>
            { this.state.variants.map(variant => (
              <Tab eventKey={this.state.dataset.name+'-'+variant.name} key={this.state.dataset.name+'-'+variant.name} title={variant.name}>
                <DatasetVariantFileList url={variant.data_list_url} />
              </Tab>
            )) }
          </Tabs>
        </Card.Body>
      </Card>
    )
  }
}

//---------------------------------------------------------------------------//

class DatasetVariantFileList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      files: []
    };
  }  

  componentDidMount() {
    fetch(this.props['url'])
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            files: result
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
      <Table>
        <thead>
          <tr>
            <th>Filename</th>
            <th>Content type</th>
            <th>Size</th>
            <th>URL</th>
          </tr>
        </thead>
        <tbody>
          { this.state.files.map(file => (
            <tr key={file.filename}>
              <td>{ file.filename }</td>
              <td>{ file.content_type }</td>
              <td>{ file.size }</td>
              <td><a href={ file.url }>Download</a></td>
            </tr>
          )) }
        </tbody>
      </Table>
    )
  }
}

//---------------------------------------------------------------------------//


class App extends Component {
  render = () => {
    return (
      <div className='row'>
        <div className='col-md-3'>
          <DatasetList url="/api/datastore/dataset" />
        </div>
        <div className='col-md-9'>
          <DatasetVariantList />
        </div>
      </div>
    );
  }
}

export default App;

{/* <Plot
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
/> */}