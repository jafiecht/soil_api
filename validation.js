//Validation Rules
/////////////////////////////////////////////////////////////////
const rules = {
  boolean: {
    trim: true,
    escape: true,
    toBoolean: true
  },
  email: {
    isEmail: true,
    normalizeEmail: true
  },
  int: {
    isInt: { options: { min: 0 } },
    trim: true,
    escape: true
  },
  float: {
    isFloat: { options: { min: 0 } },
    trim: true,
    escape: true
  },
  string: {
    trim: true,
    escape: true
  }
};


//Validation Schema
/////////////////////////////////////////////////////////////////
const TaskSchema = {
  'values.email': rules.email,
  'values.points.type': rules.string,
  'values.points.feautures.*.type': rules.string, 
  'values.points.feautures.*.properties.value': rules.float, 
  'values.points.feautures.*.geometry.type': rules.string, 
  'values.points.feautures.*.geometry.coordinates.*': rules.float, 
  'values.boundary.type': rules.string,
  'values.boundary.feautures.*.type': rules.string, 
  'values.boundary.feautures.*.properties.value': rules.float, 
  'values.boundary.feautures.*.geometry.type': rules.string, 
  'values.boundary.feautures.*.geometry.coordinates.*.*': rules.float, 
};

module.exports = {
  getTaskSchema: () => {
    return TaskSchema;
  }
};

