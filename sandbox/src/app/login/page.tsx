import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    // Handle login logic here
    console.log('Logging in:', { email, password });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-xs p-6 bg-white rounded-lg shadow-md">
        <h2 className="mb-6 text-2xl font-bold text-center">Login</h2>
        <form className="space-y-4">
          <div>
            <label htmlFor="email" className="block mb-1 font-medium">Email</label>
            <Input 
              id="email" 
              type="email" 
              placeholder="Enter your email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block mb-1 font-medium">Password</label>
            <Input 
              id="password" 
              type="password" 
              placeholder="Enter your password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <Button type="button" className="w-full bg-blue-500 text-white rounded-md py-2" onClick={handleLogin}>Login</Button>
        </form>
        <div className="flex justify-between mt-4">
          <span className="text-sm text-gray-600">Or login with</span>
          <div className="flex space-x-4">
            <Button className="bg-red-500 text-white rounded-md py-2">Google</Button>
            <Button className="bg-blue-600 text-white rounded-md py-2">Facebook</Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
