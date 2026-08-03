import { useState } from 'react'
import notebook from './assets/scrapbook.jpg'
import { drivers } from './data/drivers'
import DriverCard from './DriverCard'

const Scrapbook = () => {
  const [selectedDriver, setSelectedDriver] = useState(null)

  return (
    <div style={{
      width: '100vw',
      height: '100vh',
      backgroundImage: `url(${notebook})`,
      backgroundSize: '100% 100%',
      backgroundPosition: 'center',
      display: 'flex',
    }}>
      {/* LEFT PAGE */}
      <div style={{
        width: '50%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        {selectedDriver ? (
          <DriverCard {...selectedDriver} />
        ) : (
          <p>Click a sticker</p>
        )}
      </div>

      {/* RIGHT PAGE */}
      <div style={{ width: '50%', height: '100%', position: 'relative' }}>
        {drivers.map(driver => {
          console.log(driver.name, driver.rotate)
          return (
            <img
              key={driver.number}
              src={driver.image}
              onClick={() => setSelectedDriver(driver)}
              style={{
                position: 'absolute',
                width: '120px',
                top: driver.top,
                left: driver.left,
                cursor: 'pointer',
                transform: `rotate(${driver.rotate}deg)`,
              }}
            />
          )
        })}
      </div>
    </div>
  )
}

export default Scrapbook