# UI Component Library Documentation

## Button Component

### Usage
```jsx
import Button from '@/components/ui/Button'

<Button variant="primary" size="md" onClick={() => alert('Clicked!')}>
  Click Me
</Button>
```

### Props
- `variant`: 'primary' | 'warning' | 'success' | 'danger' | 'wine' | 'gold'
- `size`: 'sm' | 'md' | 'lg'
- `onClick`: Function to execute on click
- `children`: Button text/content

---

## Card Component

### Usage
```jsx
import Card from '@/components/ui/Card'

<Card title="My Card" variant="primary">
  <p>Card content goes here</p>
</Card>
```

### Props
- `title`: Card header text
- `variant`: 'primary' | 'warning' | 'success' | 'danger'
- `children`: Card body content

---

## Input Component

### Usage
```jsx
import Input from '@/components/ui/Input'

<Input 
  type="text"
  placeholder="Enter your name..."
  value={name}
  onChange={(e) => setName(e.target.value)}
/>
```

### Props
- `type`: 'text' | 'email' | 'password' | 'search'
- `placeholder`: Hint text
- `value`: Current value
- `onChange`: Function called on input change
- `className`: Additional CSS classes

---

## Badge Component

### Usage
```jsx
import Badge from '@/components/ui/Badge'

<Badge variant="success">Active</Badge>
<Badge variant="danger">Inactive</Badge>
```

### Props
- `variant`: 'primary' | 'warning' | 'success' | 'danger' | 'wine'
- `children`: Badge text

---

## Modal Component

### Usage
```jsx
import Modal from '@/components/ui/Modal'
import { useState } from 'react'

const [isOpen, setIsOpen] = useState(false)

<Button onClick={() => setIsOpen(true)}>Open Modal</Button>

<Modal 
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  title="Confirm Action"
>
  <p>Are you sure you want to continue?</p>
</Modal>
```

### Props
- `isOpen`: Boolean - controls visibility
- `onClose`: Function to close modal
- `title`: Modal header text
- `children`: Modal body content