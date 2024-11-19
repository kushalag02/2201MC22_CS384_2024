import { useState } from 'react'
import './App.css'
import FileUploadDownload from './FileUploader'

function App() {
  const [file, setFile] = useState(0)

  return (
    <>
      <FileUploadDownload />
    </>
  )
}

export default App
