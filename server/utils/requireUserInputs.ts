import { UserInputError } from "apollo-server-express";
type Arguments = Array<{ [key: string]: any }>;
const requireUserInputs = (userInputs: Arguments) => {
  // Get all the undefined arguments
  const undefinedNames = userInputs.filter((argument, index) => {
    const keyName = Object.keys(argument)[0];
    return !userInputs[index][keyName];
  });

  if (undefinedNames.length > 0) {
    console.warn(undefinedNames);
    throw new UserInputError("Arguments missing", {
      missingArgs: undefinedNames.map((name) => Object.keys(name)[0]),
    });
  }
};
export default requireUserInputs;
