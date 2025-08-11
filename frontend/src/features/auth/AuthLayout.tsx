type Props = {
  children: React.ReactNode;
};

export const AuthLayout = ({ children }: Props) => {
  return (
    <div className="h-screen grid grid-cols-1 md:grid-cols-2 overflow-hidden">
      <div className="hidden md:block relative">
        <img
          src="auth-bg.png"
          alt="Grocery Aisle"
          className="absolute inset-0 w-full h-full object-cover"
        />
      </div>
      <div className="flex items-center justify-center p-8 overflow-y-auto">
        <div className="w-full max-w-md">{children}</div>
      </div>
    </div>
  );
};
