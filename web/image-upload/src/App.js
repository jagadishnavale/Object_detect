import { useState } from "react";
import { saveAs } from 'file-saver'
import './App.css';

const url = 'http://localhost:8080';

function App() {
  const [image, setImage] = useState(null);
  const [xml, setXml] = useState(null);
  const [output, setOutput] = useState(null);

  // On file select (from the pop up)
  const onImageChange = (event) => {
    // Update the state
    setImage(event.target.files[0]);
    // setImage(URL.createObjectURL(event.target.files[0]));
  };

  // On file select (from the pop up)
  const onXMLChange = (event) => {
    // Update the state
    setXml(event.target.files[0]);
  };

  // On file upload (click the upload button)
  const onFileUpload = () => {

    // Create an object of formData
    const form_data = new FormData();

    // Update the formData object
    form_data.append('image', image, image.name);
    form_data.append('xml', xml, xml.name);

    console.log('form_data', form_data);

    fetch(`${url}/api/upload`, {
      method: 'POST',
      body: form_data,
      responseType: "blob"
    })
      .then(response => response.blob())
      .then(data => {
        setOutput(URL.createObjectURL(data));
        console.log('Success:', output);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  const onClear = () => {
    setImage(null);
    setXml(null);
  }

  const onDownloadCSV = () => {
    fetch(`${url}/api/files`, {
      responseType: "blob"
    })
      .then(response => response.blob())
      .then(blob => saveAs(blob, 'file.csv'))
      .catch((error) => {
        console.error('Error:', error);
      });
  }
  
  return (
    <div className="App">
      <div className="container-fluid">
        <div className="row">
          <div className="col-lg-6">
            <div className="text-left">
              <label>Select Image</label>
              <div>
                <input type="file" onChange={(e) => onImageChange(e)} />
              </div>
            </div>
            <div className="text-left">
              <label>Select XML</label>
              <div>
                <input type="file" accept='.xml' onChange={(e) => onXMLChange(e)} />
              </div>
            </div>
            <div className="text-left">
              <button className="btn btn-primary m-1" onClick={() => onFileUpload()}>Upload</button>
              <button className="btn btn-secondary m-1" onClick={() => onClear()}>Clear</button>
              <button className="btn btn-primary m-1" onClick={() => onDownloadCSV()}>Export to CSV</button>
            </div>
          </div>
          <div className="col-lg-6">
            {output && <img src={output} />}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
