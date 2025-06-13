import { useState } from 'react';
import { Button } from './components/Button';
import { Input } from './components/Input';
import { Modal } from './components/Modal';
import { LoginForm } from './components/LoginForm';

function App() {
  const [modalOpen, setModalOpen] = useState(false);
  const [inputVal, setInputVal] = useState('');

  return (
    <div className="min-h-screen bg-neutral-50 p-6 space-y-10 text-neutral-900 font-inter">
      <h1 className="text-h1">UI Component Preview</h1>

      {/* Buttons */}
      <section>
        <h2 className="text-h3 mb-2">Buttons</h2>
        <div className="space-x-4">
          <Button>Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
        </div>
      </section>

      {/* Input */}
      <section>
        <h2 className="text-h3 mb-2">Input</h2>
        <Input
          label="Name"
          placeholder="Enter your name"
          value={inputVal}
          onChange={(e) => setInputVal(e.target.value)}
        />
      </section>

      {/* Modal */}
      <section>
        <h2 className="text-h3 mb-2">Modal</h2>
        <Button onClick={() => setModalOpen(true)}>Open Modal</Button>
        <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)}>
          <p className="text-p mb-4">This is a modal! 🎉</p>
          <Button onClick={() => setModalOpen(false)}>Close</Button>
        </Modal>
      </section>

      {/* Login Form */}
      <section>
        <h2 className="text-h3 mb-2">Login Form</h2>
        <div className="max-w-sm border border-neutral-200 rounded-lg p-4">
          <LoginForm />
        </div>
      </section>
    </div>
  );
}

export default App;
