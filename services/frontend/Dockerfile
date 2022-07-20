FROM node:18-alpine
WORKDIR /opt/dap
COPY ./dap/package.json /opt/dap/
COPY ./dap/package-lock.json /opt/dap/
RUN npm i
COPY /dap/ /opt/dap/
CMD ["npm", "start"]