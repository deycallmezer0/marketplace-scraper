export interface Car {
    id: string;
    title: string;
    price: number;
    location: string;
    status: string;
    url: string;
    time_posted?: string;
    images?: string[];
    description?: string;
    about?: {
      mileage?: string;
      transmission?: string;
      color?: string;
      safety?: string;
      fuel_type?: string;
      mpg?: string;
      [key: string]: string | undefined;
    };
  }

  