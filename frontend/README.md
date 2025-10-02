## Next.js Frontend for Task Management

A modern, responsive Next.js 15 frontend application with TypeScript and Tailwind CSS for managing tasks and users.

## 🚀 Features

- **Next.js 15** with App Router and React 19
- **TypeScript** for type safety
- **Tailwind CSS** for modern, responsive design
- **JWT Authentication** with secure token management
- **Role-Based UI** - Different views for admins and regular users
- **Real-time Updates** - Automatic UI refresh on data changes
- **Responsive Design** - Works on all device sizes
- **Error Handling** - Comprehensive error states and loading indicators

## 🎯 User Interface

### Authentication Pages
- **Login** - Secure user authentication
- **Register** - New user registration with admin option

### Dashboard Features

#### Regular Users
- **My Tasks** - View, create, edit, and delete personal tasks
- Task status management (To Do, In Progress, Done)
- Real-time task updates

#### Admin Users
- **My Tasks** - Personal task management
- **All Tasks** - View and manage all users' tasks
- **All Users** - User management (promote/demote admins, delete users)

## 🛠️ Setup & Installation

### Prerequisites

- Node.js 18+
- npm or yarn

### Local Development

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API URL
   ```

4. **Start development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Access the application**
   ```
   http://localhost:3000
   ```

### Using Docker

```bash
# Development with hot-reload
docker-compose up frontend

# Production build
docker build -t task-management-frontend .
```

## 📋 Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎨 UI Components

### Core Components
- **AuthGuard** - Route protection and authentication checks
- **TaskForm** - Create and edit tasks
- **TaskList** - Display tasks with filtering
- **TaskItem** - Individual task display with actions
- **UserManagement** - Admin user management interface

### Design System
- **Tailwind CSS** utility classes
- **Custom component classes** in globals.css
- **Responsive breakpoints** for mobile/desktop
- **Loading states** and error handling
- **Consistent color scheme** and typography

## 🔐 Authentication Flow

1. **Login/Register** - Users authenticate via JWT tokens
2. **Token Storage** - Secure localStorage management
3. **Auto-redirect** - Protected routes redirect to login
4. **Role Detection** - UI adapts to user role (admin/regular)
5. **Automatic Logout** - Token expiration handling

## 📱 Responsive Design

- **Mobile-first** approach
- **Flexible layouts** that adapt to screen size
- **Touch-friendly** interfaces for mobile devices
- **Optimized navigation** for different screen sizes

## 🚀 Performance Features

- **Static Generation** where possible
- **Code Splitting** automatic with Next.js
- **Image Optimization** with Next.js Image component
- **Efficient Re-renders** with React best practices

## 🧪 Development

### Building for Production

```bash
npm run build
npm start
```

### Code Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # React components
│   │   ├── features/        # Feature-specific components
│   │   └── ui/              # Reusable UI components
│   ├── contexts/            # React contexts
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities and API client
│   └── types/               # TypeScript type definitions
└── public/                  # Static assets
```

### Key Files

- `src/app/layout.tsx` - Root layout with AuthProvider
- `src/app/page.tsx` - Home page redirect
- `src/app/dashboard/page.tsx` - Main application dashboard
- `src/contexts/AuthContext.tsx` - Authentication state management
- `src/lib/api.ts` - API client configuration

## 🔧 Customization

### Styling
- Modify `src/app/globals.css` for global styles
- Update Tailwind config for design system changes
- Custom component classes for reusable styles

### API Integration
- Configure `src/lib/api.ts` for different backend endpoints
- Add new API methods for additional endpoints
- Update TypeScript types in `src/types/index.ts`

## 🐳 Docker Deployment

### Development
```bash
docker-compose up frontend
```

### Production
```bash
docker build -t task-management-frontend .
docker run -p 3000:3000 task-management-frontend
```

## 🎯 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🔍 SEO & Accessibility

- Semantic HTML structure
- Proper ARIA labels
- Keyboard navigation support
- Meta tags and page titles
- Open Graph metadata

## 📚 Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [React Documentation](https://react.dev)
