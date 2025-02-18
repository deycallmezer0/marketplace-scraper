import { useState } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';

interface AddCarFormProps {
  onAdd: (url: string) => void;
}

const AddCarForm: React.FC<AddCarFormProps> = ({ onAdd }) => {
  const [url, setUrl] = useState<string>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onAdd(url);
      setUrl('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="add-car-form">
      <Input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter car URL"
      />
      <Button type="submit">Add Car</Button>
    </form>
  );
};

export default AddCarForm;
