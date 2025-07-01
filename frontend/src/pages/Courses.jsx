import React from 'react';
import { Card } from '../components/ui';
import { AcademicCapIcon, PlusIcon } from '@heroicons/react/24/outline';

const Courses = () => {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Courses</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage fitness courses and training programs
          </p>
        </div>
      </div>

      <Card className="p-12 text-center">
        <AcademicCapIcon className="mx-auto h-16 w-16 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">Coming Soon</h3>
        <p className="mt-2 text-gray-600">
          Course management functionality will be available in the next update.
        </p>
        <div className="mt-6">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Course (Coming Soon)
          </button>
        </div>
      </Card>
    </div>
  );
};

export default Courses;
