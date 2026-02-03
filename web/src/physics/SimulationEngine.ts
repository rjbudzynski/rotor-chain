export interface SimulationParams {
  n_rotors: number;
  j_coupling: number;
  m_field: number;
}

export interface OrderParameter {
  r: number;
  meanCos: number;
  meanSin: number;
}

export class SimulationEngine {
  public params: SimulationParams;
  public y: Float64Array; // [theta_0...theta_n-1, omega_0...omega_n-1]
  public t: number = 0;
  public substeps: number = 10;

  constructor(params: SimulationParams) {
    this.params = { ...params };
    this.y = new Float64Array(2 * params.n_rotors);
  }

  public setParams(params: Partial<SimulationParams>) {
    if (params.n_rotors !== undefined && params.n_rotors !== this.params.n_rotors) {
      this.params.n_rotors = params.n_rotors;
      this.y = new Float64Array(2 * this.params.n_rotors);
      this.t = 0;
    }
    if (params.j_coupling !== undefined) this.params.j_coupling = params.j_coupling;
    if (params.m_field !== undefined) this.params.m_field = params.m_field;
  }

  public setState(theta: number[] | Float64Array, omega?: number[] | Float64Array) {
    const n = this.params.n_rotors;
    for (let i = 0; i < n; i++) {
      this.y[i] = theta[i];
      if (omega) {
        this.y[n + i] = omega[i];
      } else {
        this.y[n + i] = 0;
      }
    }
  }

  private getAcceleration(theta: Float64Array, accel: Float64Array) {
    const n = this.params.n_rotors;
    const J = this.params.j_coupling;
    const M = this.params.m_field;

    for (let i = 0; i < n; i++) {
      const iPlus = (i + 1) % n;
      const iMinus = (i - 1 + n) % n;

      // d_omega_i/dt = -J * (sin(theta_i - theta_{i+1}) + sin(theta_i - theta_{i-1})) - M * sin(theta_i)
      accel[i] = -J * (Math.sin(theta[i] - theta[iPlus]) + Math.sin(theta[i] - theta[iMinus])) 
                 - M * Math.sin(theta[i]);
    }
  }

  public verletStep(dt: number) {
    const n = this.params.n_rotors;
    const theta = this.y.subarray(0, n);
    const omega = this.y.subarray(n, 2 * n);
    
    const accelT = new Float64Array(n);
    const accelNew = new Float64Array(n);

    // 1. v(t + dt/2) = v(t) + a(t) * dt/2
    this.getAcceleration(theta, accelT);
    for (let i = 0; i < n; i++) {
      omega[i] += accelT[i] * (dt / 2.0);
    }

    // 2. x(t + dt) = x(t) + v(t + dt/2) * dt
    for (let i = 0; i < n; i++) {
      theta[i] += omega[i] * dt;
      // Normalize theta to [-π, π) to prevent floating-point drift
      theta[i] = ((theta[i] + Math.PI) % (2 * Math.PI)) - Math.PI;
      if (theta[i] < -Math.PI) theta[i] += 2 * Math.PI;
    }

    // 3. v(t + dt) = v(t + dt/2) + a(t + dt) * dt/2
    this.getAcceleration(theta, accelNew);
    for (let i = 0; i < n; i++) {
      omega[i] += accelNew[i] * (dt / 2.0);
    }

    this.t += dt;
  }

  public step(dt: number) {
    const subDt = dt / this.substeps;
    for (let i = 0; i < this.substeps; i++) {
      this.verletStep(subDt);
    }
  }

  public getEnergy(): number {
    const n = this.params.n_rotors;
    const theta = this.y.subarray(0, n);
    const omega = this.y.subarray(n, 2 * n);
    const J = this.params.j_coupling;
    const M = this.params.m_field;

    let kinetic = 0;
    let potential = 0;
    let field = 0;

    for (let i = 0; i < n; i++) {
      kinetic += 0.5 * omega[i] * omega[i];
      
      const iPlus = (i + 1) % n;
      potential += J * (1 - Math.cos(theta[i] - theta[iPlus]));
      field -= M * Math.cos(theta[i]);
    }

    return kinetic + potential + field;
  }

  public getOrderParameter(): OrderParameter {
    const n = this.params.n_rotors;
    const theta = this.y.subarray(0, n);
    
    let sumCos = 0;
    let sumSin = 0;

    for (let i = 0; i < n; i++) {
      sumCos += Math.cos(theta[i]);
      sumSin += Math.sin(theta[i]);
    }

    const meanCos = sumCos / n;
    const meanSin = sumSin / n;
    const r = Math.sqrt(meanCos * meanCos + meanSin * meanSin);

    return { r, meanCos, meanSin };
  }

  public getKineticEnergies(): Float64Array {
    const n = this.params.n_rotors;
    const omega = this.y.subarray(n, 2 * n);
    const ke = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      ke[i] = 0.5 * omega[i] * omega[i];
    }
    return ke;
  }
}
